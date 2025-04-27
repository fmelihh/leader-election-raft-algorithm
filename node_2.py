import uvicorn
from fastapi import FastAPI

from src.raft_algorithm.api import raft_router

app = FastAPI()

app.include_router(raft_router, prefix="/raft", tags=["raft"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
