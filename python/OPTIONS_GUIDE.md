# SpeedyReader Command-Line Options Guide

Complete reference for all command-line options and usage patterns.

## Table of Contents
1. [Global Options](#global-options)
2. [Commands](#commands)
3. [Common Usage Patterns](#common-usage-patterns)
4. [Configuration File Options](#configuration-file-options)

---

## Global Options

These options can be combined with any command and override configuration file settings.

### `--range <days>`
**Purpose:** Control how many days of articles to keep and display

**Default:** 7 days (configurable in config.toml)

**Behavior:**
- Filters articles to only show those published within the specified number of days
- Older articles are automatically deleted from the database
- Applies to both TUI and CLI modes

**Examples:**
```bash
# Keep only 1 day of articles
python -m src.main --range 1

# Keep 30 days of articles
python -m src.main --range 30 --refresh

# View articles from the last 14 days
python -m src.main --range 14 --list-articles 20
```

**When to use:**
- Daily news reading: `--range 1` or `--range 2`
- Weekly catch-up: `--range 7`
- Monthly review: `--range 30`

---

### `--limit-per-feed <number>`
**Purpose:** Limit how many articles are fetched from each feed

**Default:** Unlimited (fetch all articles from feeds)

**Behavior:**
- Controls the number of articles fetched per feed during refresh
- Does NOT delete existing articles - only limits new fetches
- Useful for feeds with many articles to avoid database bloat

**Examples:**
```bash
# Fetch only the 5 most recent articles from each feed
python -m src.main --limit-per-feed 5

# Refresh with top 10 articles per feed
python -m src.main --limit-per-feed 10 --refresh

# Launch TUI showing only 3 articles per feed
python -m src.main --limit-per-feed 3
```

**When to use:**
- High-volume feeds: Limit to 5-10 articles
- Quick news scan: Limit to 3-5 articles
- Focused reading: Limit to 1-3 articles

---

### `--clear-articles`
**Purpose:** Delete ALL articles from the database before loading

**Default:** False (keep existing articles)

**Behavior:**
- Clears the entire article database on startup
- Keeps your feeds intact (doesn't delete feed subscriptions)
- Deletes summaries and saved-to-raindrop tracking for those articles
- Useful for starting fresh each session

**Examples:**
```bash
# Clear all articles and launch TUI
python -m src.main --clear-articles

# Clear articles, then fetch fresh ones with limit
python -m src.main --clear-articles --limit-per-feed 5 --refresh

# Start completely fresh every time
python -m src.main --clear-articles --limit-per-feed 5
```

**When to use:**
- **Daily reading workflow:** Start fresh each day with `--clear-articles --limit-per-feed 5`
- **Prevent database bloat:** Clear old data regularly
- **Testing:** Clean slate for testing feeds

**Important Notes:**
- This deletes ALL articles, not just old ones
- Feed subscriptions are preserved
- Combine with `--limit-per-feed` to fetch fresh articles immediately

---

## Commands

Commands specify what action to perform. Only one command can be used at a time.

### `--tui` (or no command)
**Default command** - Launches the interactive Terminal User Interface

**Examples:**
```bash
# Launch TUI (default)
python -m src.main

# Explicitly launch TUI
python -m src.main --tui

# Launch with options
python -m src.main --range 1 --limit-per-feed 5
```

**TUI Keyboard Shortcuts:**
- `j` or `↓` - Move down
- `k` or `↑` - Move up
- `r` - Refresh all feeds
- `s` - Generate AI summary for current article
- `o` - Open article in browser
- `q` - Quit

---

### `--refresh`
**Purpose:** Refresh all feeds and fetch new articles (headless mode)

**Examples:**
```bash
# Basic refresh
python -m src.main --refresh

# Refresh with custom range
python -m src.main --range 30 --refresh

# Refresh with article limit per feed
python -m src.main --limit-per-feed 10 --refresh

# Clear and refresh
python -m src.main --clear-articles --limit-per-feed 5 --refresh
```

**Use cases:**
- Cron jobs for automated feed updates
- Scheduled tasks
- Manual updates before reading

---

### `--add-feed <url>`
**Purpose:** Add a new RSS/Atom feed by URL

**Examples:**
```bash
# Add a single feed
python -m src.main --add-feed https://hnrss.org/newest

# Add and immediately fetch articles
python -m src.main --add-feed https://example.com/feed.xml
```

**Behavior:**
- Discovers and validates the feed
- Adds it to your feed list
- Fetches initial articles from the feed
- Auto-detects RSS/Atom format

---

### `--remove-feed <feed_id>`
**Purpose:** Remove a feed by its ID number

**Examples:**
```bash
# First, list feeds to find IDs
python -m src.main --list-feeds

# Remove feed with ID 3
python -m src.main --remove-feed 3
```

**Behavior:**
- Deletes the feed subscription
- Removes all articles from that feed
- Deletes associated summaries

---

### `--list-feeds`
**Purpose:** Display all subscribed feeds with their IDs

**Examples:**
```bash
# List all feeds
python -m src.main --list-feeds
```

**Output format:**
```
Feeds (3):
  [1] Supply Chain Dive
      URL: https://www.supplychaindive.com/feeds/news/
  [2] Hacker News
      URL: https://hnrss.org/newest
  [3] MIT Technology Review AI
      URL: https://www.technologyreview.com/topic/artificial-intelligence/feed/
```

---

### `--list-articles [limit]`
**Purpose:** List recent articles from all feeds

**Default limit:** 10 articles

**Examples:**
```bash
# List 10 most recent articles (default)
python -m src.main --list-articles

# List 20 most recent articles
python -m src.main --list-articles 20

# List articles with custom range
python -m src.main --range 1 --list-articles 50
```

**Output format:**
```
Recent Articles (showing 10):

  [1] Understanding Neural Networks
      Feed: MIT Technology Review AI
      URL: https://example.com/article1
      Published: 2026-01-20 10:30:00

  [2] Supply Chain Disruptions Continue
      Feed: Supply Chain Dive
      URL: https://example.com/article2
      Published: 2026-01-20 09:15:00
```

---

### `--summarize <article_id>`
**Purpose:** Generate AI summary for a specific article

**Requires:** Claude API key in config.toml

**Examples:**
```bash
# First, find article IDs
python -m src.main --list-articles 10

# Generate summary for article 5
python -m src.main --summarize 5
```

**Output format:**
```
Article: Understanding Neural Networks
URL: https://example.com/article1

Summary:
• Neural networks are computational models inspired by biological neurons
• They consist of interconnected layers that process information
• Training involves adjusting weights through backpropagation
• Applications include image recognition, NLP, and prediction tasks
```

---

### `--import <opml_file>`
**Purpose:** Import feed subscriptions from an OPML file

**Examples:**
```bash
# Import from OPML file
python -m src.main --import feeds.opml

# Import from specific path
python -m src.main --import C:\Users\Jim\Downloads\feeds.opml
```

**Behavior:**
- Reads feed URLs from OPML file
- Skips feeds already in your database
- Displays which feeds were added

---

### `--export <opml_file>`
**Purpose:** Export your feed subscriptions to an OPML file

**Examples:**
```bash
# Export to current directory
python -m src.main --export my-feeds.opml

# Export with full path
python -m src.main --export C:\Backup\speedy-reader-feeds.opml
```

**Use cases:**
- Backup your feed list
- Transfer feeds to another RSS reader
- Share your feed collection

---

## Common Usage Patterns

### Daily News Reader Workflow
**Goal:** Fresh articles every day, only top stories

```bash
# Clear old articles and fetch top 5 from each feed
python -m src.main --clear-articles --limit-per-feed 5
```

**Why this works:**
- `--clear-articles` removes yesterday's articles
- `--limit-per-feed 5` shows only the most recent stories
- You see 5 articles per feed, nothing old

---

### Weekly Catch-Up Workflow
**Goal:** Review the past week's articles

```bash
# Keep 7 days of articles, show top 10 per feed
python -m src.main --range 7 --limit-per-feed 10
```

**Why this works:**
- `--range 7` shows the last week
- `--limit-per-feed 10` prevents overwhelming volume
- Good balance of coverage and manageability

---

### Automated Refresh (Cron/Scheduled Task)
**Goal:** Keep articles updated automatically

```bash
# Refresh feeds every hour with limit
python -m src.main --limit-per-feed 10 --refresh
```

**Cron example (Linux/Mac):**
```bash
# Add to crontab: refresh every hour
0 * * * * cd /path/to/python && python -m src.main --limit-per-feed 10 --refresh
```

**Windows Task Scheduler:**
- Trigger: Hourly
- Action: Run `python -m src.main --limit-per-feed 10 --refresh`
- Start in: `C:\Users\Jim\Documents\AI Programming\A-RSS-Reader\python`

---

### First-Time Setup Workflow
**Goal:** Add feeds and fetch initial articles

```bash
# Add feeds one at a time
python -m src.main --add-feed https://hnrss.org/newest
python -m src.main --add-feed https://www.supplychaindive.com/feeds/news/

# Or import from OPML
python -m src.main --import feeds.opml

# Refresh to fetch articles
python -m src.main --limit-per-feed 10 --refresh

# Launch TUI to read
python -m src.main
```

---

### Minimal Distraction Workflow
**Goal:** Only see the absolute latest articles

```bash
# 1 day range, top 3 articles per feed, clear on startup
python -m src.main --clear-articles --range 1 --limit-per-feed 3
```

**Why this works:**
- `--clear-articles` removes all old data
- `--range 1` shows only today's articles
- `--limit-per-feed 3` keeps it minimal
- Perfect for focused morning news routine

---

## Configuration File Options

Location:
- **Linux/Mac:** `~/.config/speedy-reader/config.toml`
- **Windows:** `%APPDATA%\speedy-reader\config.toml`

### Complete Configuration Example

```toml
# Required for AI summaries
claude_api_key = "sk-ant-your-api-key-here"

# Optional: Raindrop.io integration for bookmarking
raindrop_token = "your-raindrop-token"

# Article retention period (days)
# Default: 7
# Can be overridden with --range flag
article_retention_days = 7

# Limit articles fetched per feed
# Default: null (fetch all)
# Can be overridden with --limit-per-feed flag
articles_per_feed = 10

# Default tags for Raindrop.io bookmarks
default_tags = ["rss", "news", "reading"]

# Refresh interval (used by future auto-refresh features)
refresh_interval_minutes = 30
```

### Configuration vs Command-Line Priority

**Priority order (highest to lowest):**
1. Command-line flags (`--range`, `--limit-per-feed`)
2. Configuration file (`config.toml`)
3. Default values (7 days, unlimited articles)

**Example:**
```toml
# config.toml
article_retention_days = 30
articles_per_feed = 10
```

```bash
# This will use range=7 (overrides config's 30)
# and limit=10 (uses config value)
python -m src.main --range 7
```

---

## Quick Reference Table

| Option | Purpose | Default | Example |
|--------|---------|---------|---------|
| `--range <days>` | Article age filter | 7 days | `--range 30` |
| `--limit-per-feed <n>` | Articles per feed | Unlimited | `--limit-per-feed 5` |
| `--clear-articles` | Delete all articles | Keep articles | `--clear-articles` |
| `--refresh` | Update feeds | - | `--refresh` |
| `--add-feed <url>` | Subscribe to feed | - | `--add-feed <url>` |
| `--remove-feed <id>` | Unsubscribe | - | `--remove-feed 3` |
| `--list-feeds` | Show subscriptions | - | `--list-feeds` |
| `--list-articles [n]` | Show articles | 10 | `--list-articles 20` |
| `--summarize <id>` | AI summary | - | `--summarize 5` |
| `--import <file>` | Import OPML | - | `--import feeds.opml` |
| `--export <file>` | Export OPML | - | `--export backup.opml` |
| `--tui` (default) | Launch interface | - | `--tui` |

---

## Recommended Configurations

### For Daily News Readers
```bash
# Daily command
python -m src.main --clear-articles --limit-per-feed 5

# Or set in config.toml
articles_per_feed = 5
article_retention_days = 1
```

### For Weekly Reviewers
```bash
# Weekly command
python -m src.main --range 7 --limit-per-feed 15

# Or set in config.toml
articles_per_feed = 15
article_retention_days = 7
```

### For Research/Archive
```bash
# Keep everything for 30 days
python -m src.main --range 30

# config.toml
article_retention_days = 30
# No limit on articles_per_feed
```

### For High-Volume Feeds
```bash
# Always use limits
python -m src.main --limit-per-feed 10 --refresh

# config.toml
articles_per_feed = 10
article_retention_days = 3
```

---

## Tips and Best Practices

1. **Start Fresh Daily:** Use `--clear-articles --limit-per-feed 5` for a clean slate each morning

2. **Prevent Database Bloat:** Either use `--clear-articles` regularly OR set a short `--range` (1-7 days)

3. **Manage High-Volume Feeds:** Always use `--limit-per-feed` to avoid thousands of articles

4. **Automation:** Set up cron/scheduled tasks with `--refresh` to keep feeds updated

5. **Testing Feeds:** Use `--clear-articles --add-feed <url>` to test new feeds in isolation

6. **Backup:** Regularly export with `--export` to preserve your feed list

7. **Claude API Usage:** AI summaries cost money - only use `--summarize` when needed

8. **Combine Options:** Most powerful when combining flags:
   ```bash
   python -m src.main --clear-articles --range 1 --limit-per-feed 5
   ```

---

## Getting Help

```bash
# Show help message
python -m src.main --help
python -m src.main
```

For more information, see:
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [README_PYTHON.md](README_PYTHON.md) - Full documentation
