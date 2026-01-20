"""Main entry point for SpeedyReader Python version."""

import asyncio
import sys
from pathlib import Path

from .app import App
from .config import Config


def parse_args():
    """Parse command-line arguments and return (args, range_override, limit_override, clear_articles)."""
    args = sys.argv[1:]
    range_override = None
    limit_override = None
    clear_articles = False

    # Check for --clear-articles flag
    if "--clear-articles" in args:
        clear_articles = True
        args.remove("--clear-articles")

    # Check for --range flag and extract it
    if "--range" in args:
        try:
            range_idx = args.index("--range")
            if range_idx + 1 < len(args):
                range_override = int(args[range_idx + 1])
                # Remove --range and its value from args
                args = args[:range_idx] + args[range_idx + 2:]
            else:
                print("Error: --range requires a value (number of days)")
                sys.exit(1)
        except ValueError as e:
            print(f"Error: --range value must be a number: {e}")
            sys.exit(1)

    # Check for --limit-per-feed flag and extract it
    if "--limit-per-feed" in args:
        try:
            limit_idx = args.index("--limit-per-feed")
            if limit_idx + 1 < len(args):
                limit_override = int(args[limit_idx + 1])
                # Remove --limit-per-feed and its value from args
                args = args[:limit_idx] + args[limit_idx + 2:]
            else:
                print("Error: --limit-per-feed requires a value (number of articles)")
                sys.exit(1)
        except ValueError as e:
            print(f"Error: --limit-per-feed value must be a number: {e}")
            sys.exit(1)

    return args, range_override, limit_override, clear_articles


def main_async():
    """Main function."""
    args, range_override, limit_override, clear_articles = parse_args()

    # Check for --tui flag (launch Terminal UI)
    if len(args) == 0 or (len(args) >= 1 and args[0] == "--tui"):
        # Load configuration
        config = Config.load()

        # Override retention days if --range was provided
        if range_override is not None:
            config.article_retention_days = range_override

        # Override articles per feed if --limit-per-feed was provided
        if limit_override is not None:
            config.articles_per_feed = limit_override

        from .tui import SpeedyReaderTUI
        app = SpeedyReaderTUI()
        # Pass config and clear_articles flag to TUI
        app.config_override = config
        app.clear_articles = clear_articles
        app.run()
        return

    # For CLI commands, run async
    return asyncio.run(main_cli_async(args, range_override, limit_override, clear_articles))


async def main_cli_async(args, range_override, limit_override, clear_articles):
    """Main async function for CLI commands."""
    # Load configuration
    config = Config.load()

    # Override retention days if --range was provided
    if range_override is not None:
        config.article_retention_days = range_override

    # Override articles per feed if --limit-per-feed was provided
    if limit_override is not None:
        config.articles_per_feed = limit_override

    # Check for --import flag
    if len(args) >= 2 and args[0] == "--import":
        opml_path = Path(args[1])
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
        try:
            await app.import_opml(opml_path)
            print(f"Imported feeds from {opml_path}")
        finally:
            await app.close()
        return

    # Check for --refresh flag (headless refresh)
    if len(args) >= 1 and args[0] == "--refresh":
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
        try:
            await app.refresh_feeds(limit_per_feed=config.articles_per_feed)
            print(f"Refreshed {len(app.feeds)} feeds")
        finally:
            await app.close()
        return

    # Check for --export flag
    if len(args) >= 2 and args[0] == "--export":
        opml_path = Path(args[1])
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
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
        await app.initialize(clear_articles=clear_articles)
        try:
            await app.add_feed(feed_url)
        finally:
            await app.close()
        return

    # Check for --list-feeds flag
    if len(args) >= 1 and args[0] == "--list-feeds":
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
        try:
            print(f"\nFeeds ({len(app.feeds)}):")
            for feed in app.feeds:
                print(f"  [{feed.id}] {feed.title}")
                print(f"      URL: {feed.url}")
        finally:
            await app.close()
        return

    # Check for --remove-feed flag
    if len(args) >= 2 and args[0] == "--remove-feed":
        feed_id = int(args[1])
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
        try:
            # Find the feed to confirm deletion
            feed = None
            for f in app.feeds:
                if f.id == feed_id:
                    feed = f
                    break

            if not feed:
                print(f"Feed with ID {feed_id} not found")
                return

            print(f"Removing feed: {feed.title}")
            print(f"URL: {feed.url}")
            await app.repository.delete_feed(feed_id)
            print(f"Feed {feed_id} removed successfully")
        finally:
            await app.close()
        return

    # Check for --list-articles flag
    if len(args) >= 1 and args[0] == "--list-articles":
        limit = int(args[1]) if len(args) >= 2 else 10
        app = App(config)
        await app.initialize(clear_articles=clear_articles)
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
        await app.initialize(clear_articles=clear_articles)
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
  python -m src.main [OPTIONS] [COMMAND] [ARGS]

Options:
  --range <days>                 Set article retention period (overrides config)
                                 Example: --range 30
  --limit-per-feed <number>      Limit articles fetched per feed (overrides config)
                                 Example: --limit-per-feed 10
  --clear-articles               Clear all articles on startup before loading

Commands:
  (no command) or --tui          Launch Terminal UI (default)
  --refresh                      Refresh all feeds (headless mode)
  --import <opml_file>           Import feeds from OPML file
  --export <opml_file>           Export feeds to OPML file
  --add-feed <url>               Add a new feed by URL
  --remove-feed <feed_id>        Remove a feed by ID
  --list-feeds                   List all feeds
  --list-articles [limit]        List recent articles (default: 10)
  --summarize <article_id>       Generate summary for an article

Examples:
  python -m src.main                                    # Launch TUI with default settings
  python -m src.main --clear-articles                   # Clear all articles and launch TUI
  python -m src.main --range 30                         # Launch TUI, keep articles for 30 days
  python -m src.main --limit-per-feed 10 --refresh      # Refresh, fetch only 10 articles per feed
  python -m src.main --range 14 --refresh               # Refresh feeds, keep 14 days of articles
  python -m src.main --list-articles 20                 # List 20 recent articles
  python -m src.main --clear-articles --limit-per-feed 5 --refresh  # Clear, fetch 5 per feed, refresh

Configuration:
  Edit ~/.config/speedy-reader/config.toml (or %APPDATA%/speedy-reader/config.toml on Windows)

  Required for AI summaries:
    claude_api_key = "sk-ant-..."

  Optional settings:
    raindrop_token = "..."
    article_retention_days = 7     # Default retention period (days)
    articles_per_feed = null       # Limit articles per feed (null = all)
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
