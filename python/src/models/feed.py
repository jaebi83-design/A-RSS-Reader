"""Feed model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Feed:
    """Represents an RSS feed."""

    id: int
    title: str
    url: str
    site_url: Optional[str]
    description: Optional[str]
    last_fetched: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass
class NewFeed:
    """Represents a new feed to be inserted into the database."""

    title: str
    url: str
    site_url: Optional[str]
    description: Optional[str]
