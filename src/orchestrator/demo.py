"""End-to-end demo: PYTHONPATH=src python3 -m orchestrator.demo"""
from __future__ import annotations

from .fetcher import StaticAdapter, collect
from .log import EventLog
from .models import Topic
from .publisher import DemoPublisher, publish_due
from .queue import Queue
from .review import ReviewInbox


def main() -> None:
    log = EventLog()
    inbox = ReviewInbox(log)
    queue = Queue(log)

    adapters = [
        StaticAdapter("subreddit", [Topic("subreddit", "Consistency beats intensity", "https://example.com/a")]),
        StaticAdapter("blog", [Topic("blog", "Consistency beats intensity (repost)", "https://example.com/a"),
                               Topic("blog", "Queues, not drafts", "https://example.com/b")]),
    ]
    inbox.add_topics(collect(adapters))  # the duplicate URL is deduped away

    topic = inbox.pick_list()[0]
    inbox.pick(topic)
    draft = inbox.draft_for(topic, "First draft: consistency is a system, not a mood.")
    inbox.revise(draft, "Revised draft: consistency is a system. Here is the system.")
    inbox.approve(draft)  # the only road into the queue
    queue.enqueue(draft, slot="2026-10-27T09:00")

    refs = publish_due(queue.due("2026-10-27T09:00"), DemoPublisher(), log)
    print(f"published: {refs}")
    print(log.to_jsonl())


if __name__ == "__main__":
    main()
