"""Queue stage: approved drafts take fixed publish slots.

The gate is structural: enqueue() raises for anything not APPROVED.
"""
from __future__ import annotations

from .log import EventLog
from .models import Draft, QueuedPost, Status


class NotApprovedError(RuntimeError):
    pass


class Queue:
    def __init__(self, log: EventLog) -> None:
        self._log = log
        self.posts: list[QueuedPost] = []

    def enqueue(self, draft: Draft, slot: str) -> QueuedPost:
        if draft.status is not Status.APPROVED:
            raise NotApprovedError(
                f"refusing to queue a draft in status {draft.status.value!r}; "
                "only an explicit approval can queue a post"
            )
        post = QueuedPost(draft=draft, slot=slot)
        draft.status = Status.QUEUED
        self.posts.append(post)
        self._log.record("queued", topic=draft.topic.title, slot=slot)
        return post

    def due(self, slot: str) -> list[QueuedPost]:
        return [p for p in self.posts if p.slot == slot and p.status is Status.QUEUED]
