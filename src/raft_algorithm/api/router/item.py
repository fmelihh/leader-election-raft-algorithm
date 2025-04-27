from fastapi import Depends, HTTPException

from .router import raft_router
from ...schemas.enums import StateEnum
from ...services import get_raft_node_service, RaftNodeService


@raft_router.post("/item")
async def set_item(
    key: str,
    value: str,
    raft_node_service: RaftNodeService = Depends(get_raft_node_service),
):
    if raft_node_service.state != StateEnum.LEADER:
        raise HTTPException("Invalid state", 404)

    result = await raft_node_service.set_item(key, value)
    return result


@raft_router.get("/item")
async def get_item(
    key: str, raft_node_service: RaftNodeService = Depends(get_raft_node_service)
):
    if raft_node_service.state != StateEnum.LEADER:
        raise HTTPException("Invalid state", 404)

    result = await raft_node_service.get_item(key)
    return result


@raft_router.delete("/item")
async def delete_item(
    key: str, raft_node_service: RaftNodeService = Depends(get_raft_node_service)
):
    if raft_node_service.state != StateEnum.LEADER:
        raise HTTPException("Invalid state", 404)

    result = await raft_node_service.remove_item(key)
    return result
