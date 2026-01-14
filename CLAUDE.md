# CLAUDE.md

Project-specific instructions for Claude Code.

## Build & Run

```bash
cargo build              # Dev build
cargo build --release    # Release build
cargo run                # Run TUI
cargo run -- --refresh   # Headless refresh (for cron/systemd)
cargo run -- --import feeds.opml  # Import OPML and exit
```

## Architecture

- **Async TUI**: Uses tokio + ratatui with non-blocking operations
- **Database**: SQLite via tokio-rusqlite
- **Config**: TOML at `~/.config/speedy-reader/config.toml`

## UX Principles

**Progress indicators**: If an operation blocks input for more than ~1 second, show a spinner or progress indicator so the user isn't left wondering if the app froze. Use the non-blocking pattern with channels:
1. Spawn background task with `tokio::spawn`
2. Send results via `mpsc` channel
3. Poll for results in main loop (allows UI to redraw)
4. Show animated spinner while waiting

Current spinners use braille animation: `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`

## Key Files

- `src/app.rs` - Main application state and logic
- `src/tui/ui.rs` - UI rendering
- `src/tui/handler.rs` - Key bindings
- `src/db/repository.rs` - Database operations
- `src/feed/fetcher.rs` - RSS/Atom fetching
