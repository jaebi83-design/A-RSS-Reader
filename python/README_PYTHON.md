# SpeedyReader - Python Version

A Python conversion of the Rust-based SpeedyReader RSS reader with AI-powered article summaries.

## About This Version

This is a Python port of the original Rust application. The core functionality has been preserved and enhanced with:

- **Full TUI (Terminal User Interface)**: Interactive article browsing using Textual
- **Complete CLI**: Command-line interface for all operations
- RSS/Atom feed fetching and parsing
- SQLite database for article caching
- AI-powered summaries using Claude API
- OPML import/export
- Raindrop.io integration
- Firefox cookie support for authenticated content

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Installation

### From Source

1. Clone or navigate to the repository:
```bash
cd python
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install in development mode:
```bash
pip install -e .
```

## Configuration

Create a configuration file at:
- Linux/Mac: `~/.config/speedy-reader/config.toml`
- Windows: `%APPDATA%\speedy-reader\config.toml`

Example configuration:
```toml
# Database path (optional, defaults to data directory)
db_path = "/path/to/feeds.db"

# Required for AI summaries
claude_api_key = "sk-ant-..."

# Optional: Raindrop.io integration
raindrop_token = "your-raindrop-token"

# Optional settings
refresh_interval_minutes = 30
article_retention_days = 7  # Days to keep articles (default: 7)
articles_per_feed = 10  # Limit articles per feed (null/omit = fetch all)
default_tags = ["rss", "news"]
```

## Usage

### TUI Mode (Interactive)

Launch the Terminal User Interface:

```bash
# Default mode - launches TUI
python -m src.main

# Explicitly launch TUI
python -m src.main --tui

# Launch TUI with custom article retention
python -m src.main --range 30  # Keep articles for 30 days
```

#### TUI Features
- Split-pane interface with article list and detail view
- Real-time article content and AI summary display
- Navigate with keyboard shortcuts
- Modern UI built with Textual framework

#### TUI Key Bindings

| Key | Action |
|-----|--------|
| `j`/`k` or `↓`/`↑` | Navigate articles |
| `r` | Refresh all feeds |
| `s` | Generate AI summary |
| `o` | Open article in browser |
| `q` | Quit |

### CLI Mode (Headless)

The Python version provides a comprehensive command-line interface:

#### Command-Line Options

The `--range`, `--limit-per-feed`, and `--clear-articles` options can be used with any command:

```bash
# Override article retention period
python -m src.main --range 14 --refresh

# Limit articles fetched per feed (useful for large feeds)
python -m src.main --limit-per-feed 10 --refresh

# Clear all articles and start fresh
python -m src.main --clear-articles --refresh

# Combine multiple options
python -m src.main --range 30 --limit-per-feed 10 --refresh

# Clear articles, fetch only 5 per feed, and launch TUI
python -m src.main --clear-articles --limit-per-feed 5
```

#### Refresh Feeds
```bash
python -m src.main --refresh

# With custom retention period
python -m src.main --range 30 --refresh
```

#### Import OPML File
```bash
python -m src.main --import feeds.opml
```

#### Export OPML File
```bash
python -m src.main --export my-feeds.opml
```

#### Add a New Feed
```bash
python -m src.main --add-feed https://example.com/feed.xml
```

#### Remove a Feed
First, list feeds to find the ID:
```bash
python -m src.main --list-feeds
```

Then remove by ID:
```bash
python -m src.main --remove-feed <feed_id>
```

#### List All Feeds
```bash
python -m src.main --list-feeds
```

#### List Recent Articles
```bash
# Default: show 10 articles
python -m src.main --list-articles

# Show specific number
python -m src.main --list-articles 20
```

#### Generate Summary for an Article
```bash
python -m src.main --summarize <article_id>
```

## Features

### TUI (Terminal User Interface)
- **Split-pane layout**: Article list + detail view
- **Live updates**: Content refreshes as you navigate
- **Keyboard navigation**: Vim-style (j/k) and arrow keys
- **Modern UI**: Built with Textual framework
- **Article preview**: See feed content and AI summaries side-by-side

### Feed Management
- Auto-discovery of RSS/Atom feeds from websites
- OPML import/export for feed subscriptions
- Add/remove feeds via CLI
- Automatic duplicate detection
- 7-day article retention

### AI Summaries
- Powered by Claude 3.5 Haiku
- Generates concise bullet-point summaries
- Caches summaries in the database
- Available in both TUI and CLI modes
- Configurable via Claude API key

### Raindrop.io Integration
- Save articles as bookmarks
- Include AI summaries in notes
- Automatic tagging
- Saves to "News Links" collection

### Database
- SQLite for efficient local storage
- Automatic schema initialization
- Deleted article tracking (prevents re-adding)
- Automatic cleanup of old articles

## Project Structure

```
python/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point (TUI + CLI)
│   ├── app.py               # Backend application logic
│   ├── config.py            # Configuration management
│   ├── error.py             # Error types
│   ├── models/              # Data models
│   │   ├── article.py
│   │   ├── feed.py
│   │   └── summary.py
│   ├── db/                  # Database layer
│   │   ├── repository.py
│   │   └── schema.py
│   ├── feed/                # Feed fetching
│   │   ├── fetcher.py
│   │   └── opml.py
│   ├── ai/                  # AI summarization
│   │   └── summarizer.py
│   ├── services/            # External services
│   │   ├── content_fetcher.py
│   │   └── raindrop.py
│   └── tui/                 # Terminal UI (Textual)
│       └── app.py
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README_PYTHON.md
```

## Comparison with Rust Version

### Implemented
✅ Full TUI (Terminal User Interface) with Textual
✅ Interactive article browsing
✅ Real-time content display
✅ Keyboard navigation (j/k and arrows)
✅ Visual article list and summary display
✅ All core functionality (feeds, articles, summaries)
✅ Complete command-line interface for automation
✅ Database operations
✅ API integrations (Claude, Raindrop.io)
✅ OPML import/export
✅ Feed discovery

### Python-Specific Advantages
- **Dual Interface**: Both TUI and CLI in one tool
- **Modern Framework**: Built with Textual (actively maintained)
- **Easy Extension**: Python makes customization simple
- **Cross-Platform**: No compilation needed
- **Automation-Friendly**: Rich CLI for scripting

### Rust Version Advantages
- More advanced keybindings
- Auto-mark read functionality
- Delete/undelete articles
- Day-of-week display format
- Lower memory footprint
- Faster startup time

## Example Workflows

### Interactive Reading (TUI)
```bash
# Launch TUI and browse articles interactively
python -m src.main

# Use j/k or arrows to navigate
# Press 's' to generate AI summary
# Press 'o' to open in browser
# Press 'r' to refresh feeds
```

### Automated Feed Management
```bash
# Add multiple feeds
python -m src.main --add-feed https://hnrss.org/newest
python -m src.main --add-feed https://feeds.arstechnica.com/arstechnica/index

# Refresh (ideal for cron job)
python -m src.main --refresh

# List feeds
python -m src.main --list-feeds

# Remove unwanted feed
python -m src.main --remove-feed 3

# Export backup
python -m src.main --export backup.opml
```

### Scripting and Automation
```bash
# Cron job to refresh feeds hourly
0 * * * * cd /path/to/python && python -m src.main --refresh

# Batch generate summaries
python -m src.main --list-articles 5 | \
  grep -oP '\[\K\d+' | \
  xargs -I {} python -m src.main --summarize {}
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## Dependencies

Core libraries:
- **textual**: Modern TUI framework
- **aiohttp**: Async HTTP client
- **aiosqlite**: Async SQLite interface
- **feedparser**: RSS/Atom feed parsing
- **html2text**: HTML to plain text conversion
- **tomli/tomli-w**: TOML configuration parsing
- **anthropic**: Claude API client

## Troubleshooting

### "No module named 'src'"
Make sure you're running from the `python/` directory:
```bash
cd python
python -m src.main --help
```

### "No Claude API key configured"
Add your Claude API key to the config file:
```toml
claude_api_key = "sk-ant-..."
```

Get your API key from: https://console.anthropic.com/

### Database locked errors
The application uses a busy timeout of 5 seconds. If you're still seeing lock errors:
- Make sure no other instances are running
- Close any SQLite browser tools viewing the database

### Feed parsing errors
Some feeds may use non-standard formats:
- Check the feed URL is correct and accessible
- Try accessing the URL in a browser
- Some feeds require authentication (use Firefox cookies)

### TUI display issues
If the TUI doesn't render correctly:
- Ensure your terminal supports Unicode and colors
- Try resizing the terminal window
- Use a modern terminal emulator (Windows Terminal, iTerm2, etc.)

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step beginner's guide.

## License

MIT - Same as the original Rust version

## Credits

Converted from the Rust version by leolaporte: https://github.com/leolaporte/rss-reader

Original Rust version built with [Claude Code](https://claude.ai/code).
