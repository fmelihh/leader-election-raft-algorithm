from fastapi import Depends

from .router import raft_router
from ...services import get_raft_node


@raft_router.post("/item")
async def set_item(raft_node=Depends(get_raft_node)):
    pass


@raft_router.get("/item")
async def get_item(raft_node=Depends(get_raft_node)):
    pass


@raft_router.delete("/item")
async def delete_item(raft_node=Depends(get_raft_node)):
    pass
