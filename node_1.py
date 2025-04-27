import uvicorn
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.raft_algorithm.api import raft_router
from src.raft_algorithm.services import get_raft_node_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(get_raft_node_service().election_loop())
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(raft_router, prefix="/raft", tags=["raft"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
