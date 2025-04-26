from fastapi import APIRouter


class RaftNodeRouter:
    def __init__(self, node_id: str, peers: list[str]):
        self.node_id = node_id
        self.peers = peers

        self.router = APIRouter()
        self.router.add_api_route("/hello", self.hello, methods=["GET"])

    def hello(self):
        pass


__all__ = ["RaftNodeRouter"]
