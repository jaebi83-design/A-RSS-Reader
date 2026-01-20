"""Configuration management for SpeedyReader."""

import os
import tomllib
import tomli_w
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List

from .error import ConfigError


def default_db_path() -> str:
    """Get the default database path."""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.getenv('APPDATA', Path.home())) / 'speedy-reader'
    else:  # Unix-like
        data_dir = Path.home() / '.local' / 'share' / 'speedy-reader'

    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / 'feeds.db')


def config_dir() -> Path:
    """Get the configuration directory."""
    if os.name == 'nt':  # Windows
        config_path = Path(os.getenv('APPDATA', Path.home())) / 'speedy-reader'
    else:  # Unix-like
        config_path = Path.home() / '.config' / 'speedy-reader'

    return config_path


@dataclass
class Config:
    """Application configuration."""

    db_path: str = field(default_factory=default_db_path)
    claude_api_key: Optional[str] = None
    raindrop_token: Optional[str] = None
    refresh_interval_minutes: int = 30
    article_retention_days: int = 7
    articles_per_feed: Optional[int] = None  # None = fetch all articles
    default_tags: List[str] = field(default_factory=lambda: ["rss"])

    @staticmethod
    def config_path() -> Path:
        """Get the configuration file path."""
        return config_dir() / 'config.toml'

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from file, or create default if not exists."""
        config_file = cls.config_path()

        if config_file.exists():
            try:
                with open(config_file, 'rb') as f:
                    data = tomllib.load(f)
                    return cls(**data)
            except Exception as e:
                raise ConfigError(f"Failed to load config: {e}")
        else:
            config = cls()
            config.save()
            return config

    def save(self):
        """Save configuration to file."""
        config_file = self.config_path()
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Convert to dict and remove None values (TOML can't serialize None)
            data = {k: v for k, v in asdict(self).items() if v is not None}
            with open(config_file, 'wb') as f:
                tomli_w.dump(data, f)
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")
