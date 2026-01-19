"""Error handling for SpeedyReader."""


class AppError(Exception):
    """Base exception for application errors."""

    pass


class DatabaseError(AppError):
    """Database operation error."""

    pass


class HttpError(AppError):
    """HTTP request error."""

    pass


class FeedParseError(AppError):
    """Feed parsing error."""

    pass


class OpmlParseError(AppError):
    """OPML parsing error."""

    pass


class ConfigError(AppError):
    """Configuration error."""

    pass


class ClaudeApiError(AppError):
    """Claude API error."""

    pass


class RaindropApiError(AppError):
    """Raindrop API error."""

    pass
