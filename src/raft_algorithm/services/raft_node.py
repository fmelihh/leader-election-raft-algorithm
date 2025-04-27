import os
import time
import random

from ..schemas.enums import StateEnum


class RaftNode:
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
