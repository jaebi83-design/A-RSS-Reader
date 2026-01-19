"""Feed fetching functionality."""

import asyncio
import re
from typing import List, Tuple, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
import feedparser
from html2text import html2text

from ..error import HttpError, FeedParseError
from ..models import Feed, NewArticle, NewFeed


class FeedFetcher:
    """Fetches and parses RSS/Atom feeds."""

    def __init__(self):
        """Initialize the feed fetcher."""
        self.user_agent = "speedy-reader/1.0"
        self.timeout = aiohttp.ClientTimeout(total=30, connect=10)

    async def fetch_feed(self, feed_id: int, url: str) -> List[NewArticle]:
        """Fetch and parse a feed, returning a list of articles."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.get(
                    url, headers={"User-Agent": self.user_agent}
                ) as response:
                    if not response.ok:
                        raise HttpError(f"HTTP {response.status}")

                    content = await response.read()
                    feed = feedparser.parse(content)

                    if feed.bozo and not feed.entries:
                        raise FeedParseError(f"Failed to parse feed: {feed.bozo_exception}")

                    articles = []
                    for entry in feed.entries:
                        # Extract content
                        content_html = None
                        if hasattr(entry, "content") and entry.content:
                            content_html = entry.content[0].get("value", "")
                        elif hasattr(entry, "summary"):
                            content_html = entry.summary

                        content_text = None
                        if content_html:
                            try:
                                content_text = html2text(content_html)
                            except Exception:
                                pass

                        # Extract publication date
                        published_at = None
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            from datetime import datetime
                            import time

                            published_at = datetime.fromtimestamp(
                                time.mktime(entry.published_parsed)
                            )
                        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                            from datetime import datetime
                            import time

                            published_at = datetime.fromtimestamp(
                                time.mktime(entry.updated_parsed)
                            )

                        # Extract URL
                        article_url = entry.get("link", "")

                        # Extract author
                        author = None
                        if hasattr(entry, "author"):
                            author = entry.author

                        article = NewArticle(
                            feed_id=feed_id,
                            guid=entry.get("id", entry.get("link", "")),
                            title=entry.get("title", "Untitled"),
                            url=article_url,
                            author=author,
                            content=content_html,
                            content_text=content_text,
                            published_at=published_at,
                        )
                        articles.append(article)

                    return articles

            except aiohttp.ClientError as e:
                raise HttpError(str(e))

    async def refresh_all(self, feeds: List[Feed]) -> List[Tuple[int, List[NewArticle]]]:
        """Refresh all feeds concurrently with rate limiting."""
        results = []
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent fetches

        async def fetch_with_limit(feed: Feed):
            async with semaphore:
                try:
                    articles = await self.fetch_feed(feed.id, feed.url)
                    return (feed.id, articles)
                except Exception:
                    return None

        tasks = [fetch_with_limit(feed) for feed in feeds]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if result and not isinstance(result, Exception):
                results.append(result)

        return results

    async def discover_feed(self, url: str) -> NewFeed:
        """Discover and create a feed from a URL.

        If the URL is a direct RSS/Atom feed, parse it directly.
        If it's an HTML page, look for feed links in <link> tags.
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.get(
                    url, headers={"User-Agent": self.user_agent}
                ) as response:
                    if not response.ok:
                        raise HttpError(f"HTTP {response.status}")

                    final_url = str(response.url)
                    content_type = response.headers.get("content-type", "")
                    content = await response.read()

                    # Try parsing as RSS/Atom feed first
                    feed = feedparser.parse(content)
                    if not feed.bozo or feed.entries:
                        title = feed.feed.get("title", "Untitled Feed")
                        description = feed.feed.get("description")
                        site_url = feed.feed.get("link")

                        return NewFeed(
                            title=title,
                            url=final_url,
                            site_url=site_url,
                            description=description,
                        )

                    # If content looks like HTML, search for feed links
                    if "html" in content_type or content.startswith(
                        (b"<!DOCTYPE", b"<html", b"<!doctype")
                    ):
                        html = content.decode("utf-8", errors="ignore")
                        feed_url = self._find_feed_link(html, final_url)

                        if feed_url:
                            # Fetch the discovered feed URL
                            async with session.get(
                                feed_url, headers={"User-Agent": self.user_agent}
                            ) as feed_response:
                                if feed_response.ok:
                                    feed_content = await feed_response.read()
                                    feed = feedparser.parse(feed_content)
                                    if not feed.bozo or feed.entries:
                                        title = feed.feed.get("title", "Untitled Feed")
                                        description = feed.feed.get("description")
                                        site_url = feed.feed.get("link")

                                        return NewFeed(
                                            title=title,
                                            url=feed_url,
                                            site_url=site_url,
                                            description=description,
                                        )

                    raise FeedParseError("Could not find RSS/Atom feed at this URL")

            except aiohttp.ClientError as e:
                raise HttpError(str(e))

    def _find_feed_link(self, html: str, base_url: str) -> Optional[str]:
        """Search HTML for RSS/Atom feed links."""
        # Look for <link rel="alternate" type="application/rss+xml" href="...">
        # or <link rel="alternate" type="application/atom+xml" href="...">
        patterns = [
            r'<link[^>]*rel=["\']alternate["\'][^>]*type=["\']application/(rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
            r'<link[^>]*type=["\']application/(rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                href = match.group(2)
                return self._resolve_url(href, base_url)

        return None

    def _resolve_url(self, href: str, base_url: str) -> str:
        """Resolve a potentially relative URL against a base URL."""
        if href.startswith(("http://", "https://")):
            return href
        return urljoin(base_url, href)
