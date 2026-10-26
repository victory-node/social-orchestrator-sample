"""Fetch stage: per-source adapters produce Topics; dedupe is by URL fingerprint."""
from __future__ import annotations

from typing import Iterable, Protocol

from .models import Topic


class SourceAdapter(Protocol):
    """One adapter per source type (subreddit, forum, blog, ...)."""

    name: str

    def fetch(self) -> Iterable[Topic]:
        ...


class StaticAdapter:
    """Demo adapter returning fixed topics (stands in for Firecrawl/API fetchers)."""

    def __init__(self, name: str, topics: list[Topic]) -> None:
        self.name = name
        self._topics = topics

    def fetch(self) -> Iterable[Topic]:
        return list(self._topics)


def collect(adapters: Iterable[SourceAdapter]) -> list[Topic]:
    """Fetch from every adapter and dedupe; first occurrence wins."""
    seen: set[str] = set()
    out: list[Topic] = []
    for adapter in adapters:
        for topic in adapter.fetch():
            if topic.fingerprint not in seen:
                seen.add(topic.fingerprint)
                out.append(topic)
    return out
