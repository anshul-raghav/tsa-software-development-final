from __future__ import annotations

from pydantic import BaseModel, Field


class ExploreRequest(BaseModel):
    scan_id: str
    query: str


class ExploreResponse(BaseModel):
    spoken_description: str
    referenced_region: str | None = None
    referenced_controls: list[str] = Field(default_factory=list)
