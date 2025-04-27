from pydantic import BaseModel


class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str
