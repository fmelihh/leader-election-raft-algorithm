from fastapi import Depends

from .router import raft_router
from ...schemas.raft import AppendEntriesRequest
from ...services import get_raft_node_service, RaftNodeService


@raft_router.post("/append-entries")
async def append_entries(
    append_term: AppendEntriesRequest,
    raft_node_service: RaftNodeService = Depends(get_raft_node_service),
):
    await raft_node_service.append_entries(append_term=append_term)
