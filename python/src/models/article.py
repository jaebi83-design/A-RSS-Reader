"""Article model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """Represents an RSS article."""

    id: int
    feed_id: int
    guid: str
    title: str
    url: str
    author: Optional[str]
    content: Optional[str]
    content_text: Optional[str]
    published_at: Optional[datetime]
    fetched_at: datetime
    feed_title: Optional[str]


@dataclass
class NewArticle:
    """Represents a new article to be inserted into the database."""

    feed_id: int
    guid: str
    title: str
    url: str
    author: Optional[str]
    content: Optional[str]
    content_text: Optional[str]
    published_at: Optional[datetime]
