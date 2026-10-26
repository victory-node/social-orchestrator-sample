"""Core data types for the orchestrator sample.

Statuses are the state machine: a Draft can only reach the publish queue
by passing through APPROVED, and APPROVED is only set by the review inbox.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    FETCHED = "fetched"
    PICKED = "picked"
    DRAFTED = "drafted"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUEUED = "queued"
    PUBLISHED = "published"


@dataclass
class Topic:
    source: str
    title: str
    url: str
    status: Status = Status.FETCHED

    @property
    def fingerprint(self) -> str:
        """Stable identity used for dedupe across fetch runs."""
        return hashlib.sha256(self.url.strip().lower().encode()).hexdigest()[:16]


@dataclass
class Draft:
    topic: Topic
    text: str
    revisions: int = 0
    status: Status = Status.DRAFTED
    history: list[str] = field(default_factory=list)

    def revise(self, new_text: str) -> None:
        self.history.append(self.text)
        self.text = new_text
        self.revisions += 1


@dataclass
class QueuedPost:
    draft: Draft
    slot: str  # ISO-8601 slot label, e.g. "2026-10-27T09:00"
    status: Status = Status.QUEUED
