from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Tier(StrEnum):
    READ = "READ"
    WRITE = "WRITE"
    RISKY = "RISKY"
    BLOCKED = "BLOCKED"


class TrustMode(StrEnum):
    OBSERVE = "observe"
    ASK = "ask"
    ASSIST = "assist"


class Fact(BaseModel):
    key: str
    value: str
    source: str = "user_input"


class MissingFact(BaseModel):
    key: str
    question: str
    blocking: bool = False


class Extraction(BaseModel):
    event_type: str
    facts: list[Fact] = Field(default_factory=list)
    missing: list[MissingFact] = Field(default_factory=list)


class UndoSpec(BaseModel):
    tool: str
    ref: str | None = None


class Action(BaseModel):
    id: str
    app: str
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    tier: Tier = Tier.READ
    low_risk: bool = False
    evidence_ids: list[str] = Field(default_factory=list)
    undo: UndoSpec | None = None


class Task(BaseModel):
    id: str
    title: str
    depends_on: list[str] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)


class Plan(BaseModel):
    event_id: str
    summary: str
    tasks: list[Task] = Field(default_factory=list)

    @field_validator("tasks")
    @classmethod
    def max_actions(cls, tasks: list[Task]) -> list[Task]:
        if sum(len(task.actions) for task in tasks) > 25:
            raise ValueError("a plan may contain at most 25 actions")
        return tasks


class Evidence(BaseModel):
    id: str
    source: str
    title: str
    snippet: str
    url: str | None = None
    trusted: bool = False


class CreateEventRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000)
    trust_mode: TrustMode = TrustMode.ASK


class ApprovalRequest(BaseModel):
    approved_action_ids: list[str] = Field(default_factory=list)

