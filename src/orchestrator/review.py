"""Review stage: the topic inbox, the draft/revise loop, and the approval gate.

approve() is the ONLY function in the system that sets Status.APPROVED.
"""
from __future__ import annotations

from .log import EventLog
from .models import Draft, Status, Topic


class ReviewInbox:
    def __init__(self, log: EventLog) -> None:
        self._log = log
        self.topics: list[Topic] = []
        self.drafts: list[Draft] = []

    def add_topics(self, topics: list[Topic]) -> None:
        for topic in topics:
            self.topics.append(topic)
            self._log.record("fetched", topic=topic.title, source=topic.source)

    def pick_list(self) -> list[Topic]:
        return [t for t in self.topics if t.status is Status.FETCHED]

    def pick(self, topic: Topic) -> None:
        topic.status = Status.PICKED
        self._log.record("picked", topic=topic.title)

    def draft_for(self, topic: Topic, text: str) -> Draft:
        draft = Draft(topic=topic, text=text)
        self.drafts.append(draft)
        self._log.record("drafted", topic=topic.title, revisions=0)
        return draft

    def revise(self, draft: Draft, new_text: str) -> Draft:
        draft.revise(new_text)
        self._log.record("revised", topic=draft.topic.title, revisions=draft.revisions)
        return draft

    def approve(self, draft: Draft) -> Draft:
        draft.status = Status.APPROVED
        self._log.record("approved", topic=draft.topic.title)
        return draft

    def reject(self, draft: Draft) -> Draft:
        draft.status = Status.REJECTED
        self._log.record("rejected", topic=draft.topic.title)
        return draft
