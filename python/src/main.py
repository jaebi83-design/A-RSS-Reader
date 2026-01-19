"""Main entry point for SpeedyReader Python version."""

import asyncio
import sys
from pathlib import Path

from .app import App
from .config import Config


def main_async():
    """Main function."""
    args = sys.argv[1:]

    # Check for --tui flag (launch Terminal UI)
    if len(args) == 0 or (len(args) >= 1 and args[0] == "--tui"):
        from .tui import SpeedyReaderTUI
        app = SpeedyReaderTUI()
        app.run()
        return

    # For CLI commands, run async
    return asyncio.run(main_cli_async())


async def main_cli_async():
    """Main async function for CLI commands."""
    args = sys.argv[1:]

    # Load configuration
    config = Config.load()

    # Check for --import flag
    if len(args) >= 2 and args[0] == "--import":
        opml_path = Path(args[1])
        app = App(config)
        await app.initialize()
        try:
            await app.import_opml(opml_path)
            print(f"Imported feeds from {opml_path}")
        finally:
            await app.close()
        return

    # Check for --refresh flag (headless refresh)
    if len(args) >= 1 and args[0] == "--refresh":
        app = App(config)
        await app.initialize()
        try:
            await app.refresh_feeds()
            print(f"Refreshed {len(app.feeds)} feeds")
        finally:
            await app.close()
        return

    # Check for --export flag
    if len(args) >= 2 and args[0] == "--export":
        opml_path = Path(args[1])
        app = App(config)
        await app.initialize()
        try:
            await app.export_opml(opml_path)
            print(f"Exported feeds to {opml_path}")
        finally:
            await app.close()
        return

    # Check for --add-feed flag
    if len(args) >= 2 and args[0] == "--add-feed":
        feed_url = args[1]
        app = App(config)
        await app.initialize()
        try:
            await app.add_feed(feed_url)
        finally:
            await app.close()
        return

    # Check for --list-feeds flag
    if len(args) >= 1 and args[0] == "--list-feeds":
        app = App(config)
        await app.initialize()
        try:
            print(f"\nFeeds ({len(app.feeds)}):")
            for feed in app.feeds:
                print(f"  [{feed.id}] {feed.title}")
                print(f"      URL: {feed.url}")
        finally:
            await app.close()
        return

    # Check for --list-articles flag
    if len(args) >= 1 and args[0] == "--list-articles":
        limit = int(args[1]) if len(args) >= 2 else 10
        app = App(config)
        await app.initialize()
        try:
            print(f"\nRecent Articles (showing {limit}):")
            for i, article in enumerate(app.articles[:limit]):
                print(f"\n  [{article.id}] {article.title}")
                print(f"      Feed: {article.feed_title}")
                print(f"      URL: {article.url}")
                if article.published_at:
                    print(f"      Published: {article.published_at}")
        finally:
            await app.close()
        return

    # Check for --summarize flag
    if len(args) >= 2 and args[0] == "--summarize":
        article_id = int(args[1])
        app = App(config)
        await app.initialize()
        try:
            article = app.get_article_by_id(article_id)
            if not article:
                print(f"Article {article_id} not found")
                return

            print(f"\nArticle: {article.title}")
            print(f"URL: {article.url}\n")

            summary = await app.generate_summary(article)
            if summary:
                print("Summary:")
                print(summary.content)
            else:
                print("Failed to generate summary")
        finally:
            await app.close()
        return

    # Default: show help
    print("""SpeedyReader - RSS Reader with AI Summaries (Python Version)

Usage:
  python -m src.main [COMMAND] [ARGS]

Commands:
  --refresh                      Refresh all feeds (headless mode)
  --import <opml_file>           Import feeds from OPML file
  --export <opml_file>           Export feeds to OPML file
  --add-feed <url>               Add a new feed by URL
  --list-feeds                   List all feeds
  --list-articles [limit]        List recent articles (default: 10)
  --summarize <article_id>       Generate summary for an article

Configuration:
  Edit ~/.config/speedy-reader/config.toml (or %APPDATA%/speedy-reader/config.toml on Windows)

  Required for AI summaries:
    claude_api_key = "sk-ant-..."

  Optional for Raindrop.io integration:
    raindrop_token = "..."

Note: This Python version provides core functionality via CLI.
The full TUI (Terminal User Interface) from the Rust version is not yet implemented.
To add a TUI, consider using the 'textual' library (https://textual.textualize.io/).
""")


def main():
    """Main entry point."""
    try:
        main_async()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
