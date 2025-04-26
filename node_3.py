import uvicorn
from fastapi import FastAPI

from src.raft_algorithm.api import RaftNodeRouter

app = FastAPI()

raft_node_router = RaftNodeRouter(node_id=3, peers=["8000", "8001"])
app.include_router(raft_node_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
