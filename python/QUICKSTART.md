# Quick Start Guide - SpeedyReader Python

Get up and running with SpeedyReader in 5 minutes!

## Installation

1. Make sure you have Python 3.10+ installed:
```bash
python --version
```

2. Navigate to the python directory:
```bash
cd python
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create Config File

Create the config directory and file:

**Linux/Mac:**
```bash
mkdir -p ~/.config/speedy-reader
nano ~/.config/speedy-reader/config.toml
```

**Windows:**
```bash
mkdir %APPDATA%\speedy-reader
notepad %APPDATA%\speedy-reader\config.toml
```

### 2. Add Your Claude API Key (Optional but Recommended)

For AI summaries, add your Claude API key to the config file:

```toml
claude_api_key = "sk-ant-your-key-here"

# Optional: Customize article retention (default is 7 days)
article_retention_days = 30
```

Get your API key from: https://console.anthropic.com/

> **Note:** You can use SpeedyReader without an API key, but AI summaries won't work.

## Quick Start - TUI Mode (Interactive)

### Launch the TUI

```bash
python -m src.main
```

This launches the interactive Terminal User Interface where you can browse articles.

**Advanced:** Override settings from the command line:
```bash
# Keep articles for 30 days instead of default 7
python -m src.main --range 30

# Fetch only top 10 articles per feed (useful for large feeds)
python -m src.main --limit-per-feed 10

# Clear all old articles and start fresh with top 5 per feed
python -m src.main --clear-articles --limit-per-feed 5
```

### TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `j` or `↓` | Move down |
| `k` or `↑` | Move up |
| `r` | Refresh all feeds |
| `s` | Generate AI summary |
| `o` | Open article in browser |
| `q` | Quit |

### First Steps in TUI

1. **Add feeds via CLI first** (see below) or import an OPML file
2. **Launch TUI**: `python -m src.main`
3. **Navigate**: Use `j`/`k` or arrow keys
4. **Read**: Article content appears automatically as you navigate
5. **Summarize**: Press `s` to generate an AI summary
6. **Open**: Press `o` to open article in your browser

## Quick Start - CLI Mode (Command Line)

### 1. Add Your First Feed

```bash
python -m src.main --add-feed https://hnrss.org/newest
```

Example feeds to try:
```bash
# Hacker News
python -m src.main --add-feed https://hnrss.org/newest

# Ars Technica
python -m src.main --add-feed https://feeds.arstechnica.com/arstechnica/index

# The Verge
python -m src.main --add-feed https://www.theverge.com/rss/index.xml
```

### 2. List Your Feeds

```bash
python -m src.main --list-feeds
```

Output:
```
Feeds (3):
  [1] Hacker News: Newest
      URL: https://hnrss.org/newest
  [2] Ars Technica
      URL: https://feeds.arstechnica.com/arstechnica/index
  [3] The Verge
      URL: https://www.theverge.com/rss/index.xml
```

### 3. Refresh to Fetch Articles

```bash
python -m src.main --refresh
```

### 4. View Recent Articles

```bash
python -m src.main --list-articles 10
```

Output shows article IDs and titles:
```
Recent Articles (showing 10):

  [1] Understanding Neural Networks
      Feed: Ars Technica
      URL: https://example.com/article1
      Published: 2026-01-20 10:30:00

  [2] New Python Release Announced
      Feed: Hacker News: Newest
      URL: https://example.com/article2
      Published: 2026-01-20 09:15:00
  ...
```

### 5. Generate an AI Summary

Note the article ID from the previous command, then:
```bash
python -m src.main --summarize 1
```

Output:
```
Article: Understanding Neural Networks
URL: https://example.com/article1

Summary:
• Neural networks are computational models inspired by biological neurons
• They consist of interconnected layers that process information
• Training involves adjusting weights through backpropagation
• Applications include image recognition, NLP, and prediction tasks
```

### 6. Remove a Feed (Optional)

```bash
# List feeds to find the ID
python -m src.main --list-feeds

# Remove feed by ID (e.g., ID 3)
python -m src.main --remove-feed 3
```

## Import Existing Feeds from OPML

If you have an OPML file from another RSS reader:

```bash
python -m src.main --import /path/to/feeds.opml
```

## Export Your Feeds

Create a backup of your feed subscriptions:

```bash
python -m src.main --export my-feeds.opml
```

## Complete Example Workflow

```bash
# 1. Add some popular feeds
python -m src.main --add-feed https://hnrss.org/newest
python -m src.main --add-feed https://feeds.arstechnica.com/arstechnica/index
python -m src.main --add-feed https://www.theverge.com/rss/index.xml

# 2. Refresh to fetch articles
python -m src.main --refresh

# 3. Launch TUI to browse interactively
python -m src.main

# OR use CLI mode:

# 3a. List recent articles (note the IDs)
python -m src.main --list-articles 5

# 3b. Generate summary for article ID 1
python -m src.main --summarize 1

# 4. Export your feeds for backup
python -m src.main --export my-feeds.opml
```

## Usage Patterns

### Pattern 1: Interactive Reader (TUI)

Best for: Daily reading and browsing

```bash
# Add feeds once
python -m src.main --add-feed <url>

# Launch TUI whenever you want to read
python -m src.main
```

### Pattern 2: Automated Workflow (CLI)

Best for: Automation and scripting

```bash
# Set up a cron job to refresh feeds every hour
0 * * * * cd /path/to/python && python -m src.main --refresh

# Manually check articles via CLI when needed
python -m src.main --list-articles 20
```

### Pattern 3: Hybrid Approach

Best for: Flexibility

```bash
# Use CLI for feed management
python -m src.main --add-feed <url>
python -m src.main --remove-feed 5
python -m src.main --refresh

# Use TUI for reading
python -m src.main
```

## Tips

- **Run `--refresh` regularly**: Set up a cron job or run it manually to keep articles up-to-date
- **Database location**: Auto-created in your system's data directory
- **Article retention**: Articles older than 7 days are automatically deleted (configurable)
- **Override retention**: Use `--range <days>` to temporarily change retention period
- **Find article IDs**: Use `--list-articles` to find IDs for summarization
- **TUI navigation**: The article content updates automatically as you navigate with j/k or arrows
- **No API key needed**: You can use SpeedyReader without Claude API (summaries won't work)

## Troubleshooting

### "No module named 'src'"
Make sure you're in the `python/` directory:
```bash
cd python
python -m src.main
```

### "No Claude API key configured"
This warning appears when you try to generate summaries without an API key. Add your key to the config file or use SpeedyReader without summaries.

### TUI not displaying correctly
- Make sure your terminal is large enough
- Use a modern terminal emulator (Windows Terminal, iTerm2, etc.)
- Check that your terminal supports Unicode

### No articles showing
Did you refresh the feeds?
```bash
python -m src.main --refresh
```

## Next Steps

- Read the full [README_PYTHON.md](README_PYTHON.md) for detailed documentation
- Learn about [Raindrop.io integration](README_PYTHON.md#raindropio-integration) for bookmarking
- Set up automated refresh with cron (Linux/Mac) or Task Scheduler (Windows)
- Customize your configuration in `config.toml`

## Need Help?

Run the main command without arguments to see all options:
```bash
python -m src.main
```

Enjoy reading!
