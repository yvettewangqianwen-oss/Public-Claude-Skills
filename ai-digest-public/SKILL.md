---
name: ai-digest
description: "AI content curator that generates a personalized newsletter from YouTube channels and X/Twitter accounts. Fetches recent content, uses NotebookLM for YouTube transcript analysis, scores relevance against user interests, and delivers a tiered newsletter via email + Obsidian. Use when: (1) user says /ai-digest or 'run my digest', (2) user asks 'what's new in AI', (3) user wants to catch up on AI content, (4) scheduled cron trigger."
---

# AI Digest

Curate AI content from YouTube and X/Twitter into a personalized, scored newsletter.

## Setup (First Run)

On first run, check if `~/.ai-digest-config.json` exists. If not, ask the user for:

1. **Email address** — where to send the newsletter
2. **Gmail App Password** — generate at https://myaccount.google.com/apppasswords
3. **Output directory** — Obsidian vault path or any folder for markdown files (default: `~/ai-digest/`)
4. **Frequency** — how many days between digests (default: 3)

Create the config file:
```json
{
  "email": "user@gmail.com",
  "gmail_address": "user@gmail.com",
  "gmail_app_password": "xxxx xxxx xxxx xxxx",
  "output_dir": "~/ai-digest/",
  "days": 3
}
```

Also check and prompt for customization of:
- `references/sources.yaml` — YouTube channels and X accounts to follow
- `references/user_profile.md` — interests, scoring weights, what to skip

## Prerequisites

- `yt-dlp` installed (`uv tool install yt-dlp`)
- `notebooklm-py` installed and authenticated (`pip install "notebooklm-py[browser]" && notebooklm login`)

## Workflow

### Step 1: Fetch YouTube Videos

Read `references/sources.yaml` and build the channels JSON arg. Run:

```bash
python3 scripts/fetch_youtube.py \
  --channels '[{"handle":"...","name":"..."},...]' \
  --max-videos 5
```

Output: JSON array of videos with title, URL, description per channel.

### Step 2: Process YouTube Videos via NotebookLM

1. Create one notebook: `notebooklm create "AI Digest - {date}" --json`
2. Add each YouTube URL as source: `notebooklm source add "{youtube_url}" --json`
3. Wait for all sources: `notebooklm source wait {source_id} -n {notebook_id} --timeout 600`
4. For each source, get a concise evaluation:
   ```
   notebooklm ask "In 2-3 sentences: what is this about, who is the guest, and what's the one unique insight?" -s {source_id} --json
   ```

Keep summaries concise — preserve discovery value. Think movie trailer, not plot summary.

### Step 3: Fetch X/Twitter Content

Use WebSearch for each account in `references/sources.yaml`:
```
site:x.com/{handle} AI OR "from:{handle}" recent
```
Extract key posts, threads, and announcements from the last N days (from config).

### Step 4: Score and Classify

Read `references/user_profile.md` for scoring criteria and interest weights.

For each piece of content, score across 5 dimensions (each 1-10):
- **Trend Signal**: Does this reveal where AI is heading?
- **New Product/Model**: Is a new product, model, or capability announced?
- **Investment Signal**: VC moves, fundraising, market data?
- **Use Case Value**: Real-world application you can learn from?
- **Story Uniqueness**: Is this a perspective you won't hear elsewhere?

Final score = weighted average (weights from user_profile.md, default: trend 25%, product 25%, investment 15%, use case 20%, story 15%).
Tier: Must See (8+) / Worth Watching (5-7) / Skip (<5).

### Step 5: Generate Newsletter

The newsletter must be scannable in under 2 minutes. This one must earn attention.

```markdown
# AI Digest — {date_range}

## TL;DR — Why This Issue Matters to You
{2-3 sentences in SECOND PERSON: "This week, X happened which means Y for you. If you only have 20 minutes, watch Z because..."}

## The 3 Things You Need to Know
1. **{Headline}** — {One sentence: what happened + why it matters to YOU}
2. **{Headline}** — {Same format}
3. **{Headline}** — {Same format}

---

## Must See
### {Title}
**Source**: {Channel/Account} | {tags}
**Why this scored high**: Trend {N} | Product {N} | Investment {N} | Use Case {N} | Uniqueness {N} → **{total}/10**
{One-line hook — intriguing, no spoilers}
[Watch →]({url})

---

## Worth Watching
{Same format, score breakdown included}

---

## Skip This Time
- {Title} — {one-line reason why it scored low on user's interests}
```

Save to `{output_dir}/newsletter-{YYYY-MM-DD}.md`.

### Step 6: Email Newsletter

Read config from `~/.ai-digest-config.json` for email and credentials:

```bash
python3 scripts/send_email.py \
  --to "{email}" \
  --subject "AI Digest — {date_range}" \
  --file {output_dir}/newsletter-{YYYY-MM-DD}.md
```

### Step 7: Cleanup

Delete the NotebookLM notebook to avoid clutter:
```bash
notebooklm delete -n {notebook_id} -y
```

## Cron Automation

To automate, add to crontab (adjust path and frequency):
```bash
0 8 */3 * * /path/to/claude -p "Run /ai-digest" --allowedTools '*' 2>&1 >> ~/ai-digest/cron.log
```

## Preference Learning

When the user gives feedback (e.g. "more investment news", "skip tutorial content"), update `references/user_profile.md` to refine future scoring.
