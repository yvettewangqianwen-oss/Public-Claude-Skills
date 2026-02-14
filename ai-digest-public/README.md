# AI Digest

A [Claude Code](https://claude.com/claude-code) skill that curates AI content from YouTube and X/Twitter into a personalized, scored newsletter — delivered to your email and saved as markdown.

**The problem**: You follow 10+ AI creators but can't watch everything. You need to know what's worth your time *before* you invest 30-60 minutes watching a video.

**The solution**: AI Digest fetches recent content, uses [NotebookLM](https://github.com/teng-lin/notebooklm-py) to analyze YouTube transcripts, scores each piece against your interests, and generates a newsletter with transparent scoring so you know *why* something is recommended.

## Example Output

```
## TL;DR — Why This Issue Matters to You
This was one of the biggest weeks in AI this year. OpenAI's own engineering lead
described a future where engineers manage fleets of AI agents instead of writing
code. If you only have 20 minutes, watch the Sherwin Wu interview...

## Must See
### "Engineers are becoming sorcerers" — OpenAI's Sherwin Wu
Source: Lenny's Podcast | #trend #new-product #perspective
Why this scored high: Trend 10 | Product 9 | Investment 6 | Use Case 9 | Uniqueness 10 → 9.1/10
The head of OpenAI's platform engineering describes a world where coding is
orchestration, not implementation.
Watch → https://youtube.com/watch?v=...
```

## Install

### Prerequisites

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv tool install yt-dlp
uv tool install "notebooklm-py[browser]"

# Install Chromium for NotebookLM auth
playwright install chromium

# Login to NotebookLM (opens browser)
notebooklm login
```

### Install the Skill

Copy the skill folder to your Claude Code skills directory:

```bash
cp -r ai-digest ~/.claude/skills/ai-digest
```

Or install from the .skill file:

```bash
# If you have the packaged .skill file
unzip ai-digest.skill -d ~/.claude/skills/ai-digest
```

## Setup

On first run, Claude will ask you for:

1. **Your email** — where to receive the newsletter
2. **Gmail App Password** — get one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. **Output directory** — where to save markdown files (default: `~/ai-digest/`)

### Customize Your Feed

Edit `~/.claude/skills/ai-digest/references/sources.yaml` to add/remove channels:

```yaml
youtube_channels:
  - name: "Your Favorite Channel"
    handle: "channel_handle"  # from youtube.com/@handle

x_accounts:
  - handle: "twitter_handle"
    name: "Display Name"
```

Edit `~/.claude/skills/ai-digest/references/user_profile.md` to change your interests and scoring weights.

## Usage

In Claude Code:

```
/ai-digest
```

Or just say:

```
Run my digest
What's new in AI?
```

### Automate with Cron

Run every 3 days at 8am:

```bash
0 8 */3 * * /path/to/claude -p "Run /ai-digest" --allowedTools '*' 2>&1 >> ~/ai-digest/cron.log
```

## How Scoring Works

Each piece of content is scored on 5 dimensions (1-10):

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Trend Signal | 25% | Does this reveal where AI is heading? |
| New Product/Model | 25% | Is something new announced? |
| Investment Signal | 15% | VC moves, fundraising, market data? |
| Use Case Value | 20% | Real-world application you can learn from? |
| Story Uniqueness | 15% | Perspective you won't hear elsewhere? |

Scores are shown transparently so you can see *why* something was recommended and adjust your preferences over time.

## Architecture

```
/ai-digest
├── run the skill
│
├── Step 1: yt-dlp fetches recent videos from YouTube channels
├── Step 2: NotebookLM processes transcripts + generates summaries
├── Step 3: Web search finds recent X/Twitter posts
├── Step 4: Claude scores content against your user_profile.md
├── Step 5: Newsletter generated (markdown)
├── Step 6: Email sent via Gmail SMTP
└── Step 7: NotebookLM notebook cleaned up
```

## License

MIT
