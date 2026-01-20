# CLAUDE.md

Project-specific instructions for Claude Code.

## Project Overview

SpeedyReader is an RSS reader with AI-powered summaries, available in two implementations:

1. **Rust Version** (original): Terminal UI using ratatui + tokio
2. **Python Version** (new): Terminal UI using Textual + comprehensive CLI

## Build & Run

### Rust Version

```bash
cargo build              # Dev build
cargo build --release    # Release build
cargo run                # Run TUI
cargo run -- --refresh   # Headless refresh (for cron/systemd)
cargo run -- --import feeds.opml  # Import OPML and exit
```

### Python Version

```bash
cd python
python -m src.main                    # Run TUI (default)
python -m src.main --tui              # Explicitly run TUI
python -m src.main --refresh          # Headless refresh
python -m src.main --import feeds.opml # Import OPML
python -m src.main --add-feed <url>   # Add feed
python -m src.main --remove-feed <id> # Remove feed
python -m src.main --list-feeds       # List all feeds
python -m src.main --list-articles    # List recent articles
python -m src.main --summarize <id>   # Generate AI summary
```

## Architecture

### Rust Version

- **Async TUI**: Uses tokio + ratatui with non-blocking operations
- **Database**: SQLite via tokio-rusqlite
- **Config**: TOML at `~/.config/speedy-reader/config.toml`

### Python Version

- **Async TUI**: Uses Textual framework with asyncio
- **Backend**: Async application logic with aiohttp + aiosqlite
- **Database**: SQLite via aiosqlite
- **Config**: TOML at `~/.config/speedy-reader/config.toml` (Linux/Mac) or `%APPDATA%\speedy-reader\config.toml` (Windows)

## UX Principles

**Progress indicators**: If an operation blocks input for more than ~1 second, show a spinner or progress indicator so the user isn't left wondering if the app froze. Use the non-blocking pattern with channels:

#### Rust Pattern
1. Spawn background task with `tokio::spawn`
2. Send results via `mpsc` channel
3. Poll for results in main loop (allows UI to redraw)
4. Show animated spinner while waiting

Current spinners use braille animation: `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`

#### Python Pattern
1. Update UI with status message (e.g., "Refreshing feeds...")
2. Use async/await for operations
3. Update UI when operation completes
4. Textual handles rendering automatically

## Key Files

### Rust Version

- `src/app.rs` - Main application state and logic
- `src/tui/ui.rs` - UI rendering
- `src/tui/handler.rs` - Key bindings
- `src/db/repository.rs` - Database operations
- `src/feed/fetcher.rs` - RSS/Atom fetching

### Python Version

- `python/src/main.py` - Entry point (TUI + CLI dispatch)
- `python/src/app.py` - Backend application logic
- `python/src/tui/app.py` - Textual TUI implementation
- `python/src/db/repository.py` - Database operations
- `python/src/feed/fetcher.py` - RSS/Atom fetching
- `python/src/ai/summarizer.py` - Claude API integration

## Python-Specific Notes

### TUI Implementation

The Python TUI uses Textual framework with the following components:

- `ArticleList`: Custom ListView widget for article listing
- `ArticleHeader`: Static widget showing article title and source
- `FeedContent`: Scrollable content display (HTML converted to text)
- `AISummary`: AI-generated summary display

#### Event Handling

- `on_list_view_highlighted`: Fires when cursor moves (updates detail pane)
- `on_list_view_selected`: Fires when Enter is pressed
- `action_*` methods: Handle key bindings (e.g., `action_cursor_down`)

#### Key Bindings

Defined in `BINDINGS` list:
```python
Binding("j", "cursor_down", "Down", show=False)
Binding("k", "cursor_up", "Up", show=False)
```

### CLI Implementation

All CLI commands are handled in `python/src/main.py` via async functions:
- Commands checked sequentially with `if` statements
- Each command initializes `App`, performs action, and closes cleanly
- Help text displayed when no valid command provided

### Database

- Uses aiosqlite for async SQLite operations
- Schema in `python/src/db/schema.py`
- Repository pattern in `python/src/db/repository.py`
- Automatic busy timeout of 5 seconds

### Configuration

- TOML parsing via tomli/tomli-w
- Platform-specific config paths using platformdirs
- Config class in `python/src/config.py`

## Development Guidelines

### Rust Version
- Follow existing async patterns with tokio
- Maintain non-blocking UI updates
- Use channels for background operations

### Python Version
- Use async/await consistently
- Type hints for all public functions
- Follow existing widget patterns for TUI changes
- Keep CLI and TUI code separate
- Update help text in main.py when adding commands

## Testing

### Rust
```bash
cargo test
```

### Python
```bash
cd python
pytest
```

## Common Tasks

### Adding a New CLI Command (Python)

1. Add command check in `python/src/main.py` `main_cli_async()`
2. Implement the async logic
3. Update help text in the default case
4. Test with `python -m src.main <new-command>`

### Adding a New TUI Keybinding (Python)

1. Add `Binding` to `BINDINGS` list in `python/src/tui/app.py`
2. Implement corresponding `action_*` method
3. Update documentation in README files

### Adding a Database Column (Python)

1. Update schema in `python/src/db/schema.py`
2. Add migration SQL if needed
3. Update model in `python/src/models/`
4. Update repository methods in `python/src/db/repository.py`

## Documentation Files

- `README.md` - Main project documentation (both versions)
- `python/README_PYTHON.md` - Complete Python documentation
- `python/QUICKSTART.md` - Python quick start guide
- `CLAUDE.md` - This file (developer context)
