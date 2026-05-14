# github-issue-triage-bot

Generate issue labels and maintainer-friendly reply drafts without changing GitHub state.

This is a portfolio-ready demo for the offer: "I can automate first-pass GitHub issue triage."

## Demo From Local JSON

```bash
python3 triage_bot.py --issues examples/issues.json --output triage.md
```

Sample output: [`examples/sample-triage.md`](examples/sample-triage.md)

## Demo From GitHub API

```bash
GITHUB_TOKEN=ghp_xxx python3 triage_bot.py --repo owner/repo --limit 20 --output triage.md
```

The tool only reads issues and writes a Markdown report. It does not post comments or labels.

## Paid Offer

Fixed-price starter version: `$99`.

Client gets:

- Custom label rules
- Dry-run report
- README and demo command
- One small revision after review
- Optional GitHub Actions workflow
- Optional safe posting step after review

## Custom Setup

Need this adapted to your GitHub repo?

I can customize this starter project for:

- your labels and priority rules
- issue summary and reply templates
- GitHub API integration
- GitHub Actions scheduled triage
- safe draft-only or approved posting workflows

Contact: `mxbao063@gmail.com` for a fixed-scope quote.

More details: [`CUSTOMIZATION.md`](CUSTOMIZATION.md)
