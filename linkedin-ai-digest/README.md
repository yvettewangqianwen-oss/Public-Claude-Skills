# LinkedIn AI Digest

Turn recent LinkedIn posts from AI companies into a scored, tiered digest — without logging into LinkedIn.

## What This Skill Does

Runs WebSearch against public LinkedIn company pages, WebFetches the surfaced posts, scores them against your interests, and writes a scannable markdown newsletter.

## Limitations (be honest)

LinkedIn blocks scraping and gates most content behind login. This skill uses only public, ToS-safe methods, so:

- Coverage is **best-effort**, limited to posts Google has indexed.
- Very recent posts (last 24–48h) usually won't appear yet.
- Companies with sparse public activity will show few or zero posts.
- Some posts hit a login wall — the skill falls back to the search snippet in that case.

If you need full coverage, you need LinkedIn's official API (partner-app approval required) or a paid third-party like RSS.app. This skill does not do either.

## Prerequisites

- Python 3.9+
- `PyYAML` (`pip install pyyaml`)
- Claude Code with WebSearch and WebFetch tools available

## Setup

1. Edit `references/sources.yaml` — add or remove companies. Use the LinkedIn company slug (the part after `linkedin.com/company/`).
2. Edit `references/user_profile.md` — tune scoring weights and the "Not Interested In" list.
3. (Optional) Create `~/.ai-digest-config.json` if you want email delivery:
   ```json
   {
     "email": "you@gmail.com",
     "gmail_address": "you@gmail.com",
     "gmail_app_password": "xxxx xxxx xxxx xxxx",
     "output_dir": "~/ai-digest/",
     "days": 7
   }
   ```

## Running

```bash
claude -p "Run /linkedin-ai-digest"
```

Output lands at `~/ai-digest/linkedin-digest-YYYY-MM-DD.md`.

## Cron

Weekly (Monday 8am):
```bash
0 8 * * 1 /path/to/claude -p "Run /linkedin-ai-digest" --allowedTools '*' 2>&1 >> ~/ai-digest/linkedin-cron.log
```

## Sibling Skill

Shares config and email script with [`ai-digest-public`](../ai-digest-public/). Run both to cover YouTube + X/Twitter + LinkedIn.
