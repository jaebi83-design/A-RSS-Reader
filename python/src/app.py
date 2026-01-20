"""Main application logic for SpeedyReader.

Note: This is a simplified version of the Rust TUI application.
The full TUI with ratatui/crossterm would require the 'textual' or 'rich' library in Python.
This version provides the core functionality without the terminal UI.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from .ai import Summarizer
from .config import Config
from .db import Repository
from .error import AppError
from .feed import FeedFetcher, parse_opml_file, export_opml_file
from .models import Article, Feed, NewFeed, Summary, SummaryStatus
from .services import ContentFetcher, RaindropClient


class App:
    """Main application class managing feeds, articles, and summaries."""

    def __init__(self, config: Config):
        """Initialize the application."""
        self.config = config
        self.repository: Optional[Repository] = None
        self.fetcher = FeedFetcher()
        self.summarizer = (
            Summarizer(config.claude_api_key) if config.claude_api_key else None
        )
        self.raindrop = (
            RaindropClient(config.raindrop_token) if config.raindrop_token else None
        )
        self.content_fetcher = ContentFetcher()

        self.feeds: List[Feed] = []
        self.articles: List[Article] = []
        self.current_summary: Optional[Summary] = None

    async def initialize(self, clear_articles: bool = False):
        """Initialize the application and database.

        Args:
            clear_articles: If True, delete all articles before loading
        """
        self.repository = Repository(self.config.db_path)
        await self.repository.connect()

        if clear_articles:
            # Clear all articles
            deleted = await self.repository.clear_all_articles()
            if deleted > 0:
                print(f"Cleared {deleted} articles from database")
        else:
            # Clean up old articles
            retention_days = self.config.article_retention_days
            deleted = await self.repository.delete_old_articles(retention_days)
            if deleted > 0:
                print(f"Deleted {deleted} articles older than {retention_days} days")

        # Load feeds and articles (filter by retention period)
        self.feeds = await self.repository.get_all_feeds()
        retention_days = self.config.article_retention_days
        self.articles = await self.repository.get_all_articles_sorted(max_age_days=retention_days)

    async def close(self):
        """Clean up and close the application."""
        if self.repository:
            # Compact database on exit
            retention_days = self.config.article_retention_days
            await self.repository.compact_database(retention_days)
            await self.repository.close()

    async def refresh_feeds(self, limit_per_feed: Optional[int] = None):
        """Refresh all feeds and fetch new articles.

        Args:
            limit_per_feed: Optional limit on articles per feed (None = all)
        """
        if limit_per_feed:
            print(f"Refreshing {len(self.feeds)} feeds (limit {limit_per_feed} articles per feed)...")
        else:
            print(f"Refreshing {len(self.feeds)} feeds...")

        results = await self.fetcher.refresh_all(self.feeds, limit_per_feed=limit_per_feed)

        total_new = 0
        for feed_id, articles in results:
            for article in articles:
                article_id = await self.repository.upsert_article(article)
                if article_id > 0:
                    total_new += 1

            await self.repository.update_feed_last_fetched(feed_id)

        # Reload articles (filter by retention period)
        self.articles = await self.repository.get_all_articles_sorted(max_age_days=self.config.article_retention_days)

        print(f"Added {total_new} new articles")
        return total_new

    async def add_feed(self, url: str):
        """Discover and add a new feed."""
        print(f"Discovering feed at {url}...")

        try:
            new_feed = await self.fetcher.discover_feed(url)
            feed_id = await self.repository.insert_feed(new_feed)

            print(f"Added feed: {new_feed.title}")

            # Fetch articles from the new feed
            feed = Feed(
                id=feed_id,
                title=new_feed.title,
                url=new_feed.url,
                site_url=new_feed.site_url,
                description=new_feed.description,
                last_fetched=None,
                created_at=None,
                updated_at=None,
            )
            self.feeds.append(feed)

            articles = await self.fetcher.fetch_feed(feed_id, new_feed.url)
            for article in articles:
                await self.repository.upsert_article(article)

            await self.repository.update_feed_last_fetched(feed_id)

            # Reload data
            self.feeds = await self.repository.get_all_feeds()
            self.articles = await self.repository.get_all_articles_sorted()

            print(f"Fetched {len(articles)} articles from {new_feed.title}")

        except Exception as e:
            print(f"Failed to add feed: {e}")
            raise

    async def generate_summary(self, article: Article) -> Optional[Summary]:
        """Generate a summary for an article."""
        if not self.summarizer:
            print("No Claude API key configured")
            return None

        # Check if summary already exists
        existing = await self.repository.get_summary(article.id)
        if existing:
            return existing

        print(f"Generating summary for: {article.title}")

        try:
            content = article.content_text or article.content or article.title
            summary_text = await self.summarizer.generate_summary(
                article.title, content
            )

            model_version = self.summarizer.model_version()
            await self.repository.save_summary(article.id, summary_text, model_version)

            return await self.repository.get_summary(article.id)

        except Exception as e:
            print(f"Failed to generate summary: {e}")
            return None

    async def save_to_raindrop(
        self, article: Article, summary: Optional[Summary] = None, tags: List[str] = None
    ):
        """Save an article to Raindrop.io."""
        if not self.raindrop:
            print("No Raindrop token configured")
            return

        if tags is None:
            tags = self.config.default_tags

        print(f"Saving to Raindrop: {article.title}")

        try:
            note = summary.content if summary else None

            raindrop_id = await self.raindrop.save_bookmark(
                url=article.url,
                title=article.title,
                excerpt=article.content_text[:500] if article.content_text else None,
                note=note,
                tags=tags,
            )

            await self.repository.mark_saved_to_raindrop(article.id, raindrop_id, tags)

            print(f"Saved to Raindrop with ID: {raindrop_id}")

        except Exception as e:
            print(f"Failed to save to Raindrop: {e}")
            raise

    async def import_opml(self, path: Path):
        """Import feeds from an OPML file."""
        print(f"Importing feeds from {path}...")

        feeds = parse_opml_file(path)

        added = 0
        for feed in feeds:
            try:
                # Check if feed already exists
                existing = [f for f in self.feeds if f.url == feed.url]
                if existing:
                    print(f"Skipping existing feed: {feed.title}")
                    continue

                feed_id = await self.repository.insert_feed(feed)
                added += 1
                print(f"Added: {feed.title}")

            except Exception as e:
                print(f"Failed to add {feed.title}: {e}")

        # Reload feeds
        self.feeds = await self.repository.get_all_feeds()

        print(f"Imported {added} new feeds")
        return added

    async def export_opml(self, path: Path):
        """Export feeds to an OPML file."""
        print(f"Exporting feeds to {path}...")

        export_opml_file(path, self.feeds)

        print(f"Exported {len(self.feeds)} feeds")

    async def delete_article(self, article_id: int):
        """Delete an article."""
        await self.repository.delete_article(article_id)
        self.articles = await self.repository.get_all_articles_sorted(max_age_days=self.config.article_retention_days)

    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get an article by its ID."""
        for article in self.articles:
            if article.id == article_id:
                return article
        return None
