import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from orchestrator.fetcher import StaticAdapter, collect
from orchestrator.log import EventLog
from orchestrator.models import Status, Topic
from orchestrator.publisher import DemoPublisher, publish_due
from orchestrator.queue import NotApprovedError, Queue
from orchestrator.review import ReviewInbox


def topic(title="T", url="https://example.com/x"):
    return Topic(source="test", title=title, url=url)


class TestFetch(unittest.TestCase):
    def test_dedupe_by_url(self):
        a = StaticAdapter("a", [topic(url="https://example.com/1"), topic(url="https://example.com/2")])
        b = StaticAdapter("b", [topic(url="https://EXAMPLE.com/1")])
        self.assertEqual(len(collect([a, b])), 2)


class TestApprovalGate(unittest.TestCase):
    def setUp(self):
        self.log = EventLog()
        self.inbox = ReviewInbox(self.log)
        self.queue = Queue(self.log)
        t = topic()
        self.inbox.add_topics([t])
        self.inbox.pick(t)
        self.draft = self.inbox.draft_for(t, "draft text")

    def test_unapproved_draft_cannot_queue(self):
        with self.assertRaises(NotApprovedError):
            self.queue.enqueue(self.draft, slot="2026-10-27T09:00")

    def test_rejected_draft_cannot_queue(self):
        self.inbox.reject(self.draft)
        with self.assertRaises(NotApprovedError):
            self.queue.enqueue(self.draft, slot="2026-10-27T09:00")

    def test_approved_draft_queues_and_publishes(self):
        self.inbox.approve(self.draft)
        post = self.queue.enqueue(self.draft, slot="2026-10-27T09:00")
        refs = publish_due(self.queue.due("2026-10-27T09:00"), DemoPublisher(), self.log)
        self.assertEqual(len(refs), 1)
        self.assertIs(post.status, Status.PUBLISHED)

    def test_revise_keeps_history(self):
        self.inbox.revise(self.draft, "v2")
        self.assertEqual(self.draft.revisions, 1)
        self.assertEqual(self.draft.history, ["draft text"])

    def test_every_step_is_logged(self):
        self.inbox.approve(self.draft)
        events = [e["event"] for e in self.log.events]
        self.assertEqual(events, ["fetched", "picked", "drafted", "approved"])


if __name__ == "__main__":
    unittest.main()
