---
name: linkedin-ai-digest
description: "Extracts recent LinkedIn posts from AI companies and turns them into a scored, tiered digest. Uses WebSearch + WebFetch — no LinkedIn login, public/indexed posts only. Use when: (1) user says /linkedin-ai-digest or 'run my LinkedIn digest', (2) user asks 'what are AI companies posting on LinkedIn', (3) user wants to catch up on AI company announcements, (4) scheduled cron trigger."
---

# LinkedIn AI Digest

Curate recent LinkedIn posts from a configurable list of AI companies into a scored newsletter.

## Coverage Limitations (read this first)

LinkedIn actively blocks scraping and requires authentication for most post views. This skill deliberately uses only public, ToS-safe methods:

- **WebSearch** against `site:linkedin.com/company/{slug}/posts` — surfaces posts Google has indexed.
- **WebFetch** on individual post URLs — often hits a login wall; falls back to the search snippet.

Consequences: coverage is best-effort. Very recent posts (last 24–48h), posts from companies with sparse public activity, and posts behind interstitials will be missed. The digest reports what it found; it does not pretend to be exhaustive.

## Setup (First Run)

Reuse `~/.ai-digest-config.json` from the `ai-digest` skill if it exists. If it does not, ask the user for:

1. **Email address** — where to send the digest (optional)
2. **Gmail App Password** — https://myaccount.google.com/apppasswords (only needed if emailing)
3. **Output directory** — default `~/ai-digest/`
4. **Frequency** — days between digests (default 7)

Also prompt the user to review:
- `references/sources.yaml` — LinkedIn companies to track
- `references/user_profile.md` — interests and scoring weights

## Workflow

### Step 1: Read Config

Load `references/sources.yaml` for the company list and `references/user_profile.md` for scoring weights and interests.

### Step 2: Build Fetch Plan

```bash
python3 scripts/fetch_linkedin.py \
  --companies '[{"name":"OpenAI","slug":"openai"},...]' \
  --days 7
```

Output: JSON array of `{company, slug, query, company_url}` — one entry per company. The script does **not** hit LinkedIn; it prepares the searches Claude will run.

### Step 3: Search Each Company

For each entry, run WebSearch with the prepared query. Prefer queries like:

```
site:linkedin.com/company/{slug} "posts" {last-N-days-context}
```

Collect surfaced post URLs and their snippets. Deduplicate by URL.

### Step 4: Enrich with WebFetch

For each unique post URL, call WebFetch. If the response is the LinkedIn login wall (detectable by "Sign in to view" / "Join LinkedIn" markers), fall back to the WebSearch snippet as the post body.

Extract: post text (or snippet), estimated post date, and the posting company. Discard boilerplate ("See all posts", nav chrome).

### Step 5: Score and Classify

Read `references/user_profile.md`. For each post, score across the same 5 dimensions as ai-digest:

- **Trend Signal** (1–10) — reveals where AI is heading
- **New Product/Model** (1–10) — announces a product, model, or capability
- **Investment Signal** (1–10) — funding, partnerships, market moves
- **Use Case Value** (1–10) — concrete real-world application
- **Story Uniqueness** (1–10) — perspective you won't get elsewhere

Weighted average = final score (default weights in `user_profile.md`).
Tiers: Must See (8+) / Worth Watching (5–7) / Skip (<5).

### Step 6: Generate Newsletter

Save to `{output_dir}/linkedin-digest-{YYYY-MM-DD}.md`:

```markdown
# LinkedIn AI Digest — {date_range}

## TL;DR
{2–3 sentences, second person: what happened across the tracked companies this window and why it matters to you.}

## The 3 Things You Need to Know
1. **{Headline}** — {one sentence: what + why it matters}
2. **{Headline}** — {same}
3. **{Headline}** — {same}

---

## Must See
### {Company} — {Post headline}
**Why this scored high**: Trend {N} | Product {N} | Investment {N} | Use Case {N} | Uniqueness {N} → **{total}/10**
{One-line hook}
[Read on LinkedIn →]({url})

---

## Worth Watching
{Same format, briefer hooks}

---

## Skip This Time
- {Company} — {Post headline} — {one-line reason}

---

## Coverage Notes
- Companies with 0 indexed posts this window: {list}
- Total posts surfaced: {N} across {M} companies
```

### Step 7: (Optional) Email

If the user configured email, reuse the sibling skill's mailer:

```bash
python3 ../ai-digest-public/scripts/send_email.py \
  --to "{email}" \
  --subject "LinkedIn AI Digest — {date_range}" \
  --file {output_dir}/linkedin-digest-{YYYY-MM-DD}.md
```

## Cron Automation

Weekly on Monday at 8am:
```bash
0 8 * * 1 /path/to/claude -p "Run /linkedin-ai-digest" --allowedTools '*' 2>&1 >> ~/ai-digest/linkedin-cron.log
```

## Preference Learning

When the user gives feedback ("skip hiring announcements", "more model launches"), update `references/user_profile.md` — especially the "Not Interested In" list — to refine future scoring.
