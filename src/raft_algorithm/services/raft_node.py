import os

from ..schemas.enums import StateEnum


class RaftNodeService:
    def __init__(self):
        self._id: str = os.getenv("RAFT_NODE_ID")
        self._peers: list[str] = os.getenv("RAFT_NODE_PEERS")
        self._state = StateEnum.FOLLOWER

        self._logs = []
        self._db = set()


_raft_node = None


def get_raft_node() -> RaftNodeService:
    global _raft_node
    if _raft_node is None:
        _raft_node = RaftNodeService()

    return _raft_node


__all__ = ["get_raft_node"]
