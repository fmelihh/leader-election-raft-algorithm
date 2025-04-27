from .raft_node import RaftNode


class RaftNodeService(RaftNode):
    def __init__(self):
        super().__init__()

    async def set_item(self, key: str, value: str):
        pass

    async def remove_item(self, key: str):
        pass

    async def get_item(self):
        pass


_raft_node_service = None


def get_raft_node_service() -> RaftNodeService:
    global _raft_node_service
    if _raft_node_service is None:
        _raft_node_service = RaftNodeService()

    return _raft_node_service


__all__ = ["get_raft_node_service", "RaftNodeService"]
