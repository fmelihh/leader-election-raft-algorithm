import os
import time
import httpx
import random
import asyncio
from loguru import logger

from ..schemas.enums import StateEnum
from ..schemas.raft import AppendEntriesRequest


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

        self._logs = []
        self._db = set()

    async def set_item(self, key: str, value: str):
        pass

    async def remove_item(self, key: str):
        pass

    async def get_item(self):
        pass

    async def append_entries(self, append_term: AppendEntriesRequest):
        if append_term.term >= self.current_term:
            self.current_term = append_term.term
            self.state = StateEnum.FOLLOWER
            self.last_heartbeat = asyncio.get_event_loop().time()

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
                        json={"term": self.current_term, "candidate": self._id},
                    )
                    result = response.json()
                    if result.get("vote_granted", False):
                        votes += 1
                except Exception as e:
                    logger.exception(f"Error contacting {peer}", e)

        if votes > (len(self._peers) + 1) // 2:
            self.state = StateEnum.LEADER
            logger.info(f"{self._id} Elected Leader for term {self.current_term}")
            asyncio.create_task(self.leader_heartbeat())
        else:
            self.state = StateEnum.FOLLOWER

    async def leader_heartbeat(self):
        while self.state == StateEnum.LEADER:
            async with httpx.AsyncClient() as client:
                for peer in self._peers:
                    try:
                        result = await client.post(
                            f"{peer}/append-entries",
                            json={"term": self.current_term, "leader_id": self._id},
                        )
                        result.raise_for_status()
                    except Exception as e:
                        logger.exception(f"Error sending heartbeat to {peer}", e)

                await asyncio.sleep(1.0)


_raft_node_service = None


def get_raft_node_service() -> RaftNodeService:
    global _raft_node_service
    if _raft_node_service is None:
        _raft_node_service = RaftNodeService()

    return _raft_node_service


__all__ = ["get_raft_node_service", "RaftNodeService"]
