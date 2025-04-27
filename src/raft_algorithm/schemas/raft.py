from typing import Any
from pydantic import BaseModel


class AppendEntriesRequest(BaseModel):
    term: int
    leader_id: str
    entries: list[dict[str, Any]] = []
    leader_commit: int = -1


class VoteRequest(BaseModel):
    term: int
    candidate_id: str


class LogEntryDto(BaseModel):
    term: int
    index: int
    key: str
    value: str
