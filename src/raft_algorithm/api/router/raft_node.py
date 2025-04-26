from fastapi import APIRouter

from ...schemas.enums import StateEnum


class RaftNodeRouter:
    def __init__(self, node_id: str, peers: list[str]):
        self.peers = peers
        self.node_id = node_id
        self.state = StateEnum.FOLLOWER

        self.log = []

        self.router = APIRouter()
        self.router.add_api_route("/hello", self.hello, methods=["GET"])


    def hello(self):
        pass


__all__ = ["RaftNodeRouter"]
