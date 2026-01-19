"""Database repository for feed and article operations."""

import aiosqlite
import json
from datetime import datetime
from typing import Optional, List, Tuple

from ..models import Article, Feed, NewArticle, NewFeed, Summary
from .schema import SCHEMA


def parse_datetime(s: Optional[str]) -> Optional[datetime]:
    """Parse datetime string from database."""
    if not s:
        return None
    try:
        # Try ISO format first
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try SQLite datetime format
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None


class Repository:
    """Database repository for managing feeds, articles, and summaries."""

    def __init__(self, db_path: str):
        """Initialize the repository with a database path."""
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Connect to the database and initialize schema."""
        self._conn = await aiosqlite.connect(self.db_path, timeout=5.0)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self):
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # Feed operations

    async def insert_feed(self, feed: NewFeed) -> int:
        """Insert a new feed and return its ID."""
        cursor = await self._conn.execute(
            """INSERT INTO feeds (title, url, site_url, description)
               VALUES (?, ?, ?, ?)""",
            (feed.title, feed.url, feed.site_url, feed.description),
        )
        await self._conn.commit()
        return cursor.lastrowid

    async def get_all_feeds(self) -> List[Feed]:
        """Get all feeds sorted by title."""
        cursor = await self._conn.execute(
            """SELECT id, title, url, site_url, description, last_fetched,
                      created_at, updated_at
               FROM feeds ORDER BY title"""
        )
        rows = await cursor.fetchall()
        feeds = []
        for row in rows:
            feeds.append(
                Feed(
                    id=row["id"],
                    title=row["title"],
                    url=row["url"],
                    site_url=row["site_url"],
                    description=row["description"],
                    last_fetched=parse_datetime(row["last_fetched"]),
                    created_at=parse_datetime(row["created_at"]) or datetime.now(),
                    updated_at=parse_datetime(row["updated_at"]) or datetime.now(),
                )
            )
        return feeds

    async def update_feed_last_fetched(self, feed_id: int):
        """Update the last_fetched timestamp for a feed."""
        await self._conn.execute(
            """UPDATE feeds
               SET last_fetched = datetime('now'), updated_at = datetime('now')
               WHERE id = ?""",
            (feed_id,),
        )
        await self._conn.commit()

    async def delete_feed(self, feed_id: int):
        """Delete a feed and all associated articles."""
        await self._conn.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
        await self._conn.commit()

    # Article operations

    async def upsert_article(self, article: NewArticle) -> int:
        """Insert or update an article. Returns the article ID, or 0 if skipped."""
        # Check if article was previously deleted
        cursor = await self._conn.execute(
            """SELECT 1 FROM deleted_articles
               WHERE feed_id = ? AND guid = ?""",
            (article.feed_id, article.guid),
        )
        was_deleted = await cursor.fetchone() is not None

        if was_deleted:
            return 0  # Skip deleted articles

        published_str = article.published_at.isoformat() if article.published_at else None

        cursor = await self._conn.execute(
            """INSERT INTO articles
                   (feed_id, guid, title, url, author, content, content_text, published_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(feed_id, guid) DO UPDATE SET
                   title = excluded.title,
                   url = excluded.url,
                   author = excluded.author,
                   content = excluded.content,
                   content_text = excluded.content_text,
                   published_at = excluded.published_at""",
            (
                article.feed_id,
                article.guid,
                article.title,
                article.url,
                article.author,
                article.content,
                article.content_text,
                published_str,
            ),
        )
        await self._conn.commit()
        return cursor.lastrowid

    async def get_all_articles_sorted(self) -> List[Article]:
        """Get all articles sorted by published date."""
        cursor = await self._conn.execute(
            """SELECT a.id, a.feed_id, a.guid, a.title, a.url, a.author,
                      a.content, a.content_text, a.published_at, a.fetched_at,
                      f.title as feed_title
               FROM articles a
               JOIN feeds f ON a.feed_id = f.id
               ORDER BY a.published_at DESC NULLS LAST, a.fetched_at DESC"""
        )
        rows = await cursor.fetchall()
        articles = []
        for row in rows:
            articles.append(
                Article(
                    id=row["id"],
                    feed_id=row["feed_id"],
                    guid=row["guid"],
                    title=row["title"],
                    url=row["url"],
                    author=row["author"],
                    content=row["content"],
                    content_text=row["content_text"],
                    published_at=parse_datetime(row["published_at"]),
                    fetched_at=parse_datetime(row["fetched_at"]) or datetime.now(),
                    feed_title=row["feed_title"],
                )
            )
        return articles

    async def delete_article(self, article_id: int):
        """Delete an article and record it to prevent re-adding."""
        # Record article to deleted_articles
        await self._conn.execute(
            """INSERT OR IGNORE INTO deleted_articles (feed_id, guid)
               SELECT feed_id, guid FROM articles WHERE id = ?""",
            (article_id,),
        )
        # Delete related data
        await self._conn.execute(
            "DELETE FROM summaries WHERE article_id = ?", (article_id,)
        )
        await self._conn.execute(
            "DELETE FROM saved_to_raindrop WHERE article_id = ?", (article_id,)
        )
        # Delete the article
        await self._conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
        await self._conn.commit()

    async def undelete_article(self, feed_id: int, guid: str):
        """Remove an article from the deleted list."""
        await self._conn.execute(
            "DELETE FROM deleted_articles WHERE feed_id = ? AND guid = ?",
            (feed_id, guid),
        )
        await self._conn.commit()

    async def delete_old_articles(self, days: int) -> int:
        """Delete articles older than the specified number of days."""
        # Delete related data first
        await self._conn.execute(
            """DELETE FROM summaries WHERE article_id IN (
                   SELECT id FROM articles
                   WHERE published_at < datetime('now', '-' || ? || ' days')
                      OR (published_at IS NULL AND fetched_at < datetime('now', '-' || ? || ' days'))
               )""",
            (days, days),
        )
        await self._conn.execute(
            """DELETE FROM saved_to_raindrop WHERE article_id IN (
                   SELECT id FROM articles
                   WHERE published_at < datetime('now', '-' || ? || ' days')
                      OR (published_at IS NULL AND fetched_at < datetime('now', '-' || ? || ' days'))
               )""",
            (days, days),
        )
        # Delete old articles
        cursor = await self._conn.execute(
            """DELETE FROM articles
               WHERE published_at < datetime('now', '-' || ? || ' days')
                  OR (published_at IS NULL AND fetched_at < datetime('now', '-' || ? || ' days'))""",
            (days, days),
        )
        await self._conn.commit()
        return cursor.rowcount

    async def compact_database(self, days: int) -> int:
        """Delete old articles and vacuum the database."""
        deleted = await self.delete_old_articles(days)

        # Clean up old deleted_articles tracking entries
        await self._conn.execute(
            "DELETE FROM deleted_articles WHERE deleted_at < datetime('now', '-' || ? || ' days')",
            (days,),
        )
        await self._conn.commit()

        # Vacuum to reclaim space (skip if fails - not critical)
        try:
            await self._conn.execute("VACUUM")
        except Exception:
            pass

        return deleted

    # Summary operations

    async def get_summary(self, article_id: int) -> Optional[Summary]:
        """Get the summary for an article."""
        cursor = await self._conn.execute(
            """SELECT id, article_id, content, model_version, generated_at
               FROM summaries WHERE article_id = ?""",
            (article_id,),
        )
        row = await cursor.fetchone()
        if row:
            return Summary(
                id=row["id"],
                article_id=row["article_id"],
                content=row["content"],
                model_version=row["model_version"],
                generated_at=parse_datetime(row["generated_at"]) or datetime.now(),
            )
        return None

    async def save_summary(self, article_id: int, content: str, model: str):
        """Save or update a summary for an article."""
        await self._conn.execute(
            """INSERT INTO summaries (article_id, content, model_version)
               VALUES (?, ?, ?)
               ON CONFLICT(article_id) DO UPDATE SET
                   content = excluded.content,
                   model_version = excluded.model_version,
                   generated_at = datetime('now')""",
            (article_id, content, model),
        )
        await self._conn.commit()

    # Raindrop tracking

    async def mark_saved_to_raindrop(
        self, article_id: int, raindrop_id: int, tags: List[str]
    ):
        """Mark an article as saved to Raindrop.io."""
        tags_json = json.dumps(tags)
        await self._conn.execute(
            """INSERT OR REPLACE INTO saved_to_raindrop
                   (article_id, raindrop_id, tags)
               VALUES (?, ?, ?)""",
            (article_id, raindrop_id, tags_json),
        )
        await self._conn.commit()

    async def is_saved_to_raindrop(self, article_id: int) -> bool:
        """Check if an article is saved to Raindrop.io."""
        cursor = await self._conn.execute(
            "SELECT COUNT(*) FROM saved_to_raindrop WHERE article_id = ?",
            (article_id,),
        )
        row = await cursor.fetchone()
        return row[0] > 0
