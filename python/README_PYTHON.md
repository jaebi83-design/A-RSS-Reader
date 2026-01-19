# SpeedyReader - Python Version

A Python conversion of the Rust-based SpeedyReader RSS reader with AI-powered article summaries.

## About This Version

This is a Python port of the original Rust application. The core functionality has been preserved, including:

- RSS/Atom feed fetching and parsing
- SQLite database for article caching
- AI-powered summaries using Claude API
- OPML import/export
- Raindrop.io integration
- Firefox cookie support for authenticated content

**Note:** The full Terminal User Interface (TUI) from the Rust version is not implemented in this Python version. Instead, this version provides a command-line interface. For a complete TUI experience, consider integrating with the [Textual](https://textual.textualize.io/) library.

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
default_tags = ["rss", "news"]
```

## Usage

The Python version provides a command-line interface:

### Refresh Feeds
```bash
python -m src.main --refresh
```

### Import OPML File
```bash
python -m src.main --import feeds.opml
```

### Export OPML File
```bash
python -m src.main --export my-feeds.opml
```

### Add a New Feed
```bash
python -m src.main --add-feed https://example.com/feed.xml
```

### List All Feeds
```bash
python -m src.main --list-feeds
```

### List Recent Articles
```bash
python -m src.main --list-articles 20
```

### Generate Summary for an Article
```bash
python -m src.main --summarize <article_id>
```

## Features

### Feed Management
- Auto-discovery of RSS/Atom feeds from websites
- OPML import/export for feed subscriptions
- Automatic duplicate detection
- 7-day article retention

### AI Summaries
- Powered by Claude 3.5 Haiku
- Generates concise bullet-point summaries
- Caches summaries in the database
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
│   ├── main.py              # Entry point and CLI
│   ├── app.py               # Main application logic
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
│   └── services/            # External services
│       ├── content_fetcher.py
│       └── raindrop.py
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README_PYTHON.md
```

## Differences from Rust Version

### Not Implemented
- Full TUI (Terminal User Interface) with ratatui/crossterm
- Interactive article browsing
- Real-time feed refresh in the UI
- Keyboard navigation
- Visual article list and summary display

### Implemented
- All core functionality (feeds, articles, summaries)
- Command-line interface for all operations
- Database operations
- API integrations (Claude, Raindrop.io)
- OPML import/export
- Feed discovery

### Potential Future Enhancements
- Full TUI using [Textual](https://textual.textualize.io/)
- Web interface using Flask/FastAPI
- REST API for remote access
- Multi-user support
- RSS-to-email functionality

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

- **aiohttp**: Async HTTP client
- **aiosqlite**: Async SQLite interface
- **feedparser**: RSS/Atom feed parsing
- **html2text**: HTML to plain text conversion
- **tomli/tomli-w**: TOML configuration parsing

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

### Database locked errors
The application uses a busy timeout of 5 seconds. If you're still seeing lock errors, make sure no other instances are running.

### Feed parsing errors
Some feeds may use non-standard formats. Check the feed URL is correct and accessible.

## License

MIT - Same as the original Rust version

## Credits

Converted from the Rust version by leolaporte: https://github.com/leolaporte/rss-reader

Original Rust version built with [Claude Code](https://claude.ai/code).
