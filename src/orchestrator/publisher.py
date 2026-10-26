"""Publish stage: one publisher module per channel (LinkedIn first)."""
from __future__ import annotations

from typing import Protocol

from .log import EventLog
from .models import QueuedPost, Status


class Publisher(Protocol):
    channel: str

    def publish(self, post: QueuedPost) -> str:
        """Publish and return the platform's post id/URL."""
        ...


class DemoPublisher:
    """Stands in for a real channel publisher (e.g. wrapped LinkedIn scripts)."""

    channel = "demo"

    def publish(self, post: QueuedPost) -> str:
        return f"demo://{post.slot}/{abs(hash(post.draft.text)) % 10**8}"


def publish_due(posts: list[QueuedPost], publisher: Publisher, log: EventLog) -> list[str]:
    published: list[str] = []
    for post in posts:
        ref = publisher.publish(post)
        post.status = Status.PUBLISHED
        post.draft.status = Status.PUBLISHED
        log.record("published", topic=post.draft.topic.title, ref=ref, channel=publisher.channel)
        published.append(ref)
    return published
