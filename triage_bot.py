#!/usr/bin/env python3
"""Create a dry-run triage report for GitHub issues."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Issue:
    number: int
    title: str
    body: str
    url: str


LABEL_RULES = {
    "bug": ("bug", "broken", "crash", "error", "exception", "fail", "regression"),
    "documentation": ("docs", "documentation", "readme", "guide", "setup"),
    "automation": ("automation", "bot", "script", "workflow", "csv", "excel", "api"),
    "enhancement": ("add", "feature", "support", "improve", "request"),
    "question": ("how do i", "question", "help", "unclear"),
}


def issue_text(issue: Issue) -> str:
    return f"{issue.title}\n{issue.body}".lower()


def suggest_labels(issue: Issue) -> list[str]:
    text = issue_text(issue)
    labels = [label for label, keywords in LABEL_RULES.items() if any(keyword in text for keyword in keywords)]

    if "bug" in labels and not any(keyword in text for keyword in ("steps", "reproduce", "expected", "actual")):
        labels.append("needs-repro")
    if not labels:
        labels.append("needs-triage")
    if len(issue.body.strip()) < 40:
        labels.append("needs-details")
    return labels


def draft_reply(issue: Issue, labels: list[str]) -> str:
    if "needs-repro" in labels:
        return "Thanks for reporting this. Could you add reproduction steps, expected behavior, actual behavior, and environment details?"
    if "documentation" in labels:
        return "Thanks. This looks documentation-related. A focused README or setup guide update would be a good next step."
    if "automation" in labels:
        return "Thanks. This looks like a good automation candidate. Please confirm the input, output, and desired schedule or trigger."
    if "bug" in labels:
        return "Thanks for the report. I can look for the smallest failing case and propose a focused fix with a regression test."
    return "Thanks. I marked this for triage and will clarify the expected outcome before implementation."


def normalize_issue(raw: dict) -> Issue:
    return Issue(
        number=int(raw.get("number", 0)),
        title=str(raw.get("title", "")).strip(),
        body=str(raw.get("body") or "").strip(),
        url=str(raw.get("html_url", "")).strip(),
    )


def load_issues(path: Path) -> list[Issue]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [normalize_issue(item) for item in data]


def fetch_issues(repo: str, limit: int, state: str) -> list[Issue]:
    query = urllib.parse.urlencode({"state": state, "per_page": min(limit, 100)})
    request = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?{query}")
    token = os.getenv("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return [normalize_issue(item) for item in data if "pull_request" not in item][:limit]


def build_report(issues: list[Issue]) -> str:
    lines = [
        "# GitHub Issue Triage Report",
        "",
        "| Issue | Suggested Labels | Draft Reply |",
        "| --- | --- | --- |",
    ]
    for issue in issues:
        labels = suggest_labels(issue)
        issue_label = f"#{issue.number} {issue.title}".strip()
        if issue.url:
            issue_label = f"[{issue_label}]({issue.url})"
        reply = draft_reply(issue, labels).replace("|", "\\|")
        lines.append(f"| {issue_label} | {', '.join(labels)} | {reply} |")
    lines.extend(["", "Review all suggestions before posting labels or comments to GitHub."])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a dry-run GitHub issue triage report.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--issues", type=Path, help="Path to a JSON array of GitHub issue objects.")
    source.add_argument("--repo", help="GitHub repo in owner/name format.")
    parser.add_argument("--state", default="open", choices=("open", "closed", "all"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("triage.md"))
    args = parser.parse_args()

    issues = load_issues(args.issues) if args.issues else fetch_issues(args.repo, args.limit, args.state)
    args.output.write_text(build_report(issues), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
