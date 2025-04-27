import os
import time
import httpx
import random
import asyncio
from typing import Any
from loguru import logger

from ..schemas.enums import StateEnum
from ..schemas.raft import AppendEntriesRequest, VoteRequest, LogEntryDto


class RaftNodeService:
    def __init__(self):
        self._id = os.getenv("RAFT_NODE_ID")
        self._peers = [
            f"http://localhost:{port}/raft"
            for port in os.getenv("RAFT_NODE_PEERS").split(",")
        ]

        self.votes = 0
        self.voted_for = None
        self.current_term = 0
        self.state = StateEnum.FOLLOWER
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(1.0, 3.0)

        self._logs: list[LogEntryDto] = []

        self._db = dict()
        self._commit_index = -1

        self._next_index = {}
        self._match_index = {}

        self._lock = asyncio.Lock()

    async def set_item(self, key: str, value: str):
        new_entry = LogEntryDto(
            term=self.current_term, index=len(self._logs), key=key, value=value
        )

        async with self._lock:
            self._logs.append(new_entry)

        await self._replicate_log()

    async def remove_item(self, key: str):
        await self.set_item(key, None)

    async def get_item(self, key: str) -> str | None:
        if key not in self._db:
            return

        return self._db[key]

    async def _replicate_log(self):
        for peer in self._peers:
            await self._send_append_entries(peer)

        match_indexes = list(self._match_index.values()) + [len(self._logs) - 1]
        match_indexes.sort()
        majority_match_index = match_indexes[(len(self._peers) + 1) // 2]

        async with self._lock:
            if majority_match_index > self._commit_index:
                self._commit_index = majority_match_index
                logger.info(f"Committed index advanced to {self._commit_index}")

                for i in range(self._commit_index + 1):
                    e = self._logs[i]
                    self._db[e.key] = e.value

    async def _send_append_entries(self, peer: str):
        async with self._lock:
            next_idx = self._next_index.get(peer, len(self._logs))
            entries = [e.model_dump() for e in self._logs[next_idx:]]

        payload = {
            "term": self.current_term,
            "leader_id": self._id,
            "entries": entries,
            "leader_commit": self._commit_index,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{peer}/append-entries", json=payload)
                result = response.json()

                if result.get("success", False):
                    async with self._lock:
                        self._match_index[peer] = next_idx + len(entries) - 1
                        self._next_index[peer] = self._match_index[peer] + 1
                else:
                    async with self._lock:
                        self._next_index[peer] = max(0, self._next_index[peer] - 1)

                logger.info(
                    f"Replication to {peer} {'success' if result.get('success') else 'fail'}"
                )

            except Exception as e:
                logger.exception(f"Exception while replicating logs to {peer}", e)

    async def append_entries(self, append_term: AppendEntriesRequest):
        if append_term.term < self.current_term:
            return {"term": self.current_term, "success": False}

        async with self._lock:
            self.current_term = append_term.term
            self.state = StateEnum.FOLLOWER
            self.last_heartbeat = asyncio.get_event_loop().time()

            for entry in append_term.entries:
                log_entry = LogEntryDto(**entry)
                if log_entry.index < len(self._logs):
                    self._logs[log_entry.index] = log_entry
                else:
                    self._logs.append(log_entry)

            self._commit_index = append_term.leader_commit

            for i in range(self._commit_index + 1):
                e = self._logs[i]
                self._db[e.key] = e.value

        return {"term": self.current_term, "success": True}

    async def request_vote(self, vote: VoteRequest) -> dict[str, Any]:
        if vote.term > self.current_term:
            self.current_term = vote.term
            self.voted_for = None
            self.state = StateEnum.FOLLOWER

        vote_granted = False
        if (
            self.voted_for is None or self.voted_for == vote.candidate_id
        ) and vote.term >= self.current_term:
            self.voted_for = vote.candidate_id
            vote_granted = True

        return {"term": self.current_term, "vote_granted": vote_granted}

    async def get_status(self) -> dict[str, Any]:
        return {
            "node_id": self._id,
            "state": self.state.value,
            "current_term": self.current_term,
            "voted_for": self.voted_for,
            "commit_index": self._commit_index,
        }

    async def election_loop(self):
        while True:
            await asyncio.sleep(0.5)
            now = asyncio.get_event_loop().time()

            if self.state == StateEnum.FOLLOWER and (
                now - self.last_heartbeat > self.election_timeout
            ):
                await self._start_election()

    async def _start_election(self):
        self.state = StateEnum.CANDIDATE
        self.current_term += 1
        self.voted_for = self._id

        votes = 1
        logger.info(f"{self._id} Starting election for term {self.current_term}")
        async with httpx.AsyncClient() as client:
            for peer in self._peers:
                try:
                    response = await client.post(
                        f"{peer}/request-vote",
                        json={"term": self.current_term, "candidate_id": self._id},
                    )
                    result = response.json()
                    if result.get("vote_granted", False):
                        votes += 1
                except Exception as e:
                    logger.exception(f"Error contacting {peer}", e)

        if votes > (len(self._peers) + 1) // 2:
            self.state = StateEnum.LEADER
            logger.info(f"{self._id} Elected Leader for term {self.current_term}")

            self._next_index = {peer: len(self._logs) for peer in self._peers}
            self._match_index = {peer: -1 for peer in self._peers}

            asyncio.create_task(self.leader_heartbeat())
        else:
            self.state = StateEnum.FOLLOWER

    async def leader_heartbeat(self):
        while self.state == StateEnum.LEADER:
            for peer in self._peers:
                await self._send_append_entries(peer)

            await asyncio.sleep(1.0)


_raft_node_service = None


def get_raft_node_service() -> RaftNodeService:
    global _raft_node_service
    if _raft_node_service is None:
        _raft_node_service = RaftNodeService()

    return _raft_node_service


__all__ = ["get_raft_node_service", "RaftNodeService"]
