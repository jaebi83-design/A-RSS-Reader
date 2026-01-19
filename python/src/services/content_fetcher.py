"""Content fetching with browser cookie support."""

import os
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from html2text import html2text


USER_AGENT_STRING = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"


class ContentFetcher:
    """Fetches full article content using browser cookies."""

    def __init__(self):
        """Initialize the content fetcher."""
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def fetch_full_content(self, article_url: str) -> Optional[str]:
        """Fetch full article content using browser cookies."""
        try:
            parsed = urlparse(article_url)
            domain = parsed.hostname
            if not domain:
                return None

            # Get cookies for this domain from Firefox
            cookies = self._get_firefox_cookies(domain)

            headers = {"User-Agent": USER_AGENT_STRING}
            if cookies:
                headers["Cookie"] = cookies

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(article_url, headers=headers) as response:
                    if not response.ok:
                        return None

                    html = await response.text()
                    content = self._extract_content(html)
                    return content

        except Exception:
            return None

    def _get_firefox_cookies(self, domain: str) -> str:
        """Read cookies from Firefox for a given domain."""
        try:
            firefox_profile = self._find_firefox_profile()
            if not firefox_profile:
                return ""

            cookies_db = firefox_profile / "cookies.sqlite"
            if not cookies_db.exists():
                return ""

            # Copy database to temp location (Firefox locks it)
            temp_db = Path(tempfile.gettempdir()) / "speedy-reader-cookies.sqlite"
            shutil.copy2(cookies_db, temp_db)

            try:
                conn = sqlite3.connect(str(temp_db))
                cursor = conn.cursor()

                # Query cookies for this domain
                cursor.execute(
                    "SELECT name, value FROM moz_cookies WHERE host LIKE ? OR host LIKE ?",
                    (f"%{domain}", domain),
                )

                cookies = [f"{name}={value}" for name, value in cursor.fetchall()]
                conn.close()

                return "; ".join(cookies)

            finally:
                # Clean up temp file
                if temp_db.exists():
                    temp_db.unlink()

        except Exception:
            return ""

    def _find_firefox_profile(self) -> Optional[Path]:
        """Find the default Firefox profile directory."""
        home = Path.home()

        # Check common Firefox profile locations
        if os.name == "nt":  # Windows
            firefox_dir = home / "AppData" / "Roaming" / "Mozilla" / "Firefox"
        else:  # Unix-like
            firefox_dir = home / ".mozilla" / "firefox"

        if not firefox_dir.exists():
            return None

        # Look for profiles.ini
        profiles_ini = firefox_dir / "profiles.ini"
        if profiles_ini.exists():
            try:
                content = profiles_ini.read_text()
                current_path = None
                is_default = False

                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("Path="):
                        current_path = line[5:]
                    if line == "Default=1":
                        is_default = True
                    if line.startswith("[") and line != "[General]":
                        if is_default and current_path:
                            profile_dir = firefox_dir / current_path
                            if profile_dir.exists():
                                return profile_dir
                        current_path = None
                        is_default = False

                # Check last section
                if is_default and current_path:
                    profile_dir = firefox_dir / current_path
                    if profile_dir.exists():
                        return profile_dir

            except Exception:
                pass

        # Fallback: find any profile directory with cookies.sqlite
        try:
            for entry in firefox_dir.iterdir():
                if entry.is_dir() and (entry / "cookies.sqlite").exists():
                    return entry
        except Exception:
            pass

        return None

    def _extract_content(self, html_content: str) -> Optional[str]:
        """Extract readable content from HTML."""
        try:
            text = html2text(html_content)

            # Clean up the text
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned = "\n".join(lines)

            if len(cleaned) > 200:
                return cleaned
            return None

        except Exception:
            return None
