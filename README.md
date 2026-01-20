# SpeedyReader

A terminal-based RSS reader with AI-powered article summaries.

Built for personal use, entirely vibe coded with [Claude Code](https://claude.com/claude-code).

## Available Versions

This project is available in two implementations:

- **Rust Version** (original): Full-featured TUI with advanced keybindings
- **Python Version** (new): Modern TUI using Textual + comprehensive CLI interface

See below for installation and usage of each version.

## Features

### Common Features (Both Versions)
- **Claude API integration**: Concise bullet-point summaries of articles
- **Feed discovery**: Add feeds by URL with automatic RSS/Atom detection
- **Raindrop.io integration**: Bookmark articles with AI summary in notes
- **OPML import/export**: Import and export feed subscriptions
- **SQLite caching**: Offline reading with 7-day retention

### Rust Version (Original)
- **Advanced TUI**: Split-pane with extensive keybindings
- **Day-of-week display**: Articles prefixed with publication day (Mon, Tue, etc.)
- **Delete/Undelete**: Remove articles with undo support
- **Auto-compaction**: Database cleaned and vacuumed on exit
- **Auto-mark read**: Articles marked read after 2 seconds

### Python Version (New)
- **Modern TUI**: Built with Textual framework for interactive article browsing
- **CLI Interface**: Full command-line control for automation
- **Feed Management**: Add/remove feeds via CLI
- **Article Listing**: View and filter articles from command line

---

## Rust Version

### Installation

Requires Rust 1.70+:

```bash
git clone https://github.com/leolaporte/rss-reader.git
cd rss-reader
cargo install --path .
```

### Configuration

Create `~/.config/speedy-reader/config.toml`:

```toml
# Required for AI summaries
claude_api_key = "sk-ant-..."

# Optional: Raindrop.io integration
raindrop_token = "..."
```

### Usage

```bash
# Run the TUI
speedy-reader

# Import OPML subscriptions
speedy-reader --import feeds.opml

# Headless refresh (for cron/systemd)
speedy-reader --refresh
```

### Key Bindings

| Key | Action |
|-----|--------|
| `j`/`k` or `↓`/`↑` | Navigate articles |
| `Enter` | Generate/show summary |
| `r` | Refresh all feeds |
| `a` | Add new feed |
| `i` | Import OPML file |
| `w` | Export OPML file |
| `s` | Toggle starred |
| `m` | Toggle read/unread |
| `o` | Open in browser |
| `e` | Email article |
| `b` | Bookmark to Raindrop.io |
| `f` | Cycle filter (Unread/Starred/All) |
| `g` | Regenerate summary |
| `d` | Delete article |
| `u` | Undelete last deleted |
| `?` | Show help |
| `q` | Quit |

### Systemd Timer (Auto-refresh)

To refresh feeds automatically every hour:

```bash
# Copy service files
mkdir -p ~/.config/systemd/user
cp systemd/*.{service,timer} ~/.config/systemd/user/

# Enable timer
systemctl --user enable --now speedy-reader-refresh.timer
```

---

## Python Version

### Installation

Requires Python 3.10+:

```bash
cd python
pip install -r requirements.txt
```

Or install in development mode:
```bash
pip install -e .
```

### Configuration

Create a configuration file at:
- Linux/Mac: `~/.config/speedy-reader/config.toml`
- Windows: `%APPDATA%\speedy-reader\config.toml`

Example configuration:
```toml
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

### Usage

#### TUI Mode (Interactive)

```bash
# Launch the TUI (default)
python -m src.main

# Or explicitly
python -m src.main --tui

# With custom article retention period
python -m src.main --range 30
```

#### TUI Key Bindings

| Key | Action |
|-----|--------|
| `j`/`k` or `↓`/`↑` | Navigate articles |
| `r` | Refresh all feeds |
| `s` | Generate AI summary |
| `o` | Open in browser |
| `q` | Quit |

#### CLI Mode (Headless)

All commands support the `--range`, `--limit-per-feed`, and `--clear-articles` options:

```bash
# Refresh all feeds
python -m src.main --refresh

# Refresh with custom retention (keep 30 days)
python -m src.main --range 30 --refresh

# Fetch only top 10 articles per feed
python -m src.main --limit-per-feed 10 --refresh

# Clear all articles and start fresh with top 5 per feed
python -m src.main --clear-articles --limit-per-feed 5

# Import OPML file
python -m src.main --import feeds.opml

# Export OPML file
python -m src.main --export my-feeds.opml

# Add a new feed
python -m src.main --add-feed https://example.com/feed.xml

# Remove a feed by ID
python -m src.main --remove-feed 3

# List all feeds
python -m src.main --list-feeds

# List recent articles (default: 10)
python -m src.main --list-articles 20

# Generate summary for an article
python -m src.main --summarize <article_id>
```

### Quick Start (Python)

See [python/QUICKSTART.md](python/QUICKSTART.md) for a step-by-step guide.

### Detailed Documentation (Python)

See [python/README_PYTHON.md](python/README_PYTHON.md) for complete Python documentation.

---

## Choosing a Version

### Use the Rust Version if you want:
- Maximum performance
- Smallest memory footprint
- Advanced keybindings and workflow
- Mature, battle-tested implementation

### Use the Python Version if you want:
- Modern, maintainable codebase
- CLI automation capabilities
- Easy customization and extension
- Cross-platform compatibility without compilation

---

## License

MIT
