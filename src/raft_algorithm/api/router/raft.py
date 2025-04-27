from fastapi import Depends

from .router import raft_router
from ...schemas.raft import AppendEntriesRequest, VoteRequest
from ...services import get_raft_node_service, RaftNodeService


@raft_router.post("/append-entries")
async def append_entries(
    append_term: AppendEntriesRequest,
    raft_node_service: RaftNodeService = Depends(get_raft_node_service),
):
    await raft_node_service.append_entries(append_term=append_term)


@raft_router.post("/request-vote")
async def request_vote(
    vote: VoteRequest,
    raft_node_service: RaftNodeService = Depends(get_raft_node_service),
):
    result = await raft_node_service.request_vote(vote=vote)
    return result


@raft_router.get("/status")
async def status(
    raft_node_service: RaftNodeService = Depends(get_raft_node_service),
):
    result = await raft_node_service.get_status()
    return result
