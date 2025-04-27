from pydantic import BaseModel


class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str


class VoteRequest(BaseModel):
    term: int
    candidate_id: str
