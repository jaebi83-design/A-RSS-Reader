"""Summary model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class SummaryStatus(Enum):
    """Status of an article summary."""

    NOT_GENERATED = auto()
    GENERATING = auto()
    GENERATED = auto()
    FAILED = auto()
    NO_API_KEY = auto()


@dataclass
class Summary:
    """Represents an AI-generated article summary."""

    id: int
    article_id: int
    content: str
    model_version: str
    generated_at: datetime
