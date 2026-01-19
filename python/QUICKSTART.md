# Quick Start Guide

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

## First Steps

### 1. Configure API Key (Optional, for AI summaries)

Create config file:
- **Linux/Mac**: `~/.config/speedy-reader/config.toml`
- **Windows**: `%APPDATA%\speedy-reader\config.toml`

Add your Claude API key:
```toml
claude_api_key = "sk-ant-your-key-here"
```

### 2. Add Your First Feed

```bash
python -m src.main --add-feed https://hnrss.org/newest
```

### 3. List Your Feeds

```bash
python -m src.main --list-feeds
```

### 4. Refresh to Get Articles

```bash
python -m src.main --refresh
```

### 5. View Recent Articles

```bash
python -m src.main --list-articles 10
```

### 6. Generate a Summary

Note the article ID from the previous command, then:
```bash
python -m src.main --summarize 1
```

## Import Existing Feeds

If you have an OPML file from another RSS reader:
```bash
python -m src.main --import /path/to/feeds.opml
```

## Example Workflow

```bash
# Add some popular feeds
python -m src.main --add-feed https://hnrss.org/newest
python -m src.main --add-feed https://feeds.arstechnica.com/arstechnica/index

# Refresh to fetch articles
python -m src.main --refresh

# List recent articles (note the IDs)
python -m src.main --list-articles 5

# Generate summary for article ID 1
python -m src.main --summarize 1

# Export your feeds for backup
python -m src.main --export my-feeds.opml
```

## Tips

- Run `--refresh` periodically (or set up a cron job) to fetch new articles
- The database is stored in your system's data directory
- Articles older than 7 days are automatically deleted
- Use `--list-articles` to find article IDs for summarization

## Need Help?

Run the main command without arguments to see all options:
```bash
python -m src.main
```

See README_PYTHON.md for complete documentation.
