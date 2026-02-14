---
name: ai-digest
description: "AI content curator that generates a personalized newsletter from YouTube channels and X/Twitter accounts. Fetches recent content, uses NotebookLM for YouTube transcript analysis, scores relevance against user interests (trends, products, models, investments, use cases), and pushes a tiered newsletter to Notion. Use when: (1) user says /ai-digest or 'run my digest', (2) user asks 'what's new in AI', (3) user wants to catch up on AI content, (4) scheduled cron trigger every 3 days."
---

# AI Digest

Curate AI content from YouTube and X/Twitter into a personalized newsletter pushed to Notion.

## Prerequisites

- `yt-dlp` installed (`uv tool install yt-dlp`)
- NotebookLM authenticated: `notebooklm status`
- Notion MCP connected: `claude mcp add --transport http notion https://mcp.notion.com/mcp`

Content sources: `references/sources.yaml`
User preferences: `references/user_profile.md`

## Workflow

### Step 1: Fetch YouTube Videos

Read `references/sources.yaml` and build the channels JSON arg. Run:

```bash
python3 scripts/fetch_youtube.py \
  --channels '[{"handle":"lennyspodcast","name":"Lenny'\''s Podcast"},{"handle":"ycombinator","name":"Y Combinator"},...]' \
  --max-videos 5
```

Output: JSON array of videos with title, URL, description per channel.

### Step 2: Process YouTube Videos via NotebookLM

1. Create one notebook: `notebooklm create "AI Digest - {date}" --json`
2. Add each YouTube URL as source: `notebooklm source add "{youtube_url}" --json`
3. Wait for all sources (use subagent: `notebooklm source wait {source_id} -n {notebook_id}`)
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
Extract key posts, threads, and announcements from the last 3 days.

### Step 4: Score and Classify

Read `references/user_profile.md` for scoring criteria.

For each piece of content assign:
- **Score** (1-10) based on user interest match
- **Tier**: Must See (9-10) / Worth Watching (6-8) / Skip (1-5)
- **Hook**: One line — intriguing, no spoilers
- **Tags**: `#new-model` `#investment` `#trend` `#use-case` `#perspective`

### Step 5: Generate Newsletter

```markdown
# AI Digest — {date_range}

## What Happened
- {3-5 bullet executive summary of biggest stories}

---

## Must See
### {Title}
**Source**: {Channel/Account} | **Score**: {N}/10 | {tags}
{One-line hook}
[Watch →]({url})

---

## Worth Watching
{Same format, briefer hooks}

---

## Skip This Time
- {Title} — {one-line reason}
```

Save to `~/ai-digest/newsletter-{YYYY-MM-DD}.md`.

### Step 6: Cleanup

Delete the NotebookLM notebook to avoid clutter:
```bash
notebooklm delete {notebook_id}
```

## Cron Automation

To run every 3 days at 8am:
```bash
0 8 */3 * * claude -p "Run /ai-digest" --allowedTools '*' 2>&1 >> ~/ai-digest/cron.log
```

## Preference Learning

When the user gives feedback (e.g. "more investment news", "skip tutorial content"), update `references/user_profile.md` to refine future scoring.
