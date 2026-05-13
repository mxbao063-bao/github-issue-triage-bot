import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from triage_bot import Issue, build_report, draft_reply, suggest_labels


class TriageBotTests(unittest.TestCase):
    def test_bug_without_repro_gets_needs_repro(self):
        issue = Issue(1, "Crash on upload", "It throws an exception.", "")
        labels = suggest_labels(issue)
        self.assertIn("bug", labels)
        self.assertIn("needs-repro", labels)

    def test_automation_reply_mentions_input_output(self):
        issue = Issue(2, "Add CSV automation", "Create a weekly bot for CSV files.", "")
        labels = suggest_labels(issue)
        reply = draft_reply(issue, labels)
        self.assertIn("input, output", reply)

    def test_report_contains_issue_rows(self):
        issue = Issue(3, "README setup docs", "Need setup documentation.", "https://example.com")
        report = build_report([issue])
        self.assertIn("[#3 README setup docs](https://example.com)", report)
        self.assertIn("documentation", report)


if __name__ == "__main__":
    unittest.main()
