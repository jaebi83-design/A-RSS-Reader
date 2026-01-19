"""Raindrop.io integration for bookmarking articles."""

import aiohttp
from typing import Optional, List

from ..error import RaindropApiError


RAINDROP_API_URL = "https://api.raindrop.io/rest/v1"
NEWS_COLLECTION_NAME = "News Links"


class RaindropClient:
    """Client for saving bookmarks to Raindrop.io."""

    def __init__(self, access_token: str):
        """Initialize the Raindrop client with an access token."""
        self.access_token = access_token
        self.timeout = aiohttp.ClientTimeout(total=30)
        self._news_collection_id: Optional[int] = None

    async def get_news_collection_id(self) -> Optional[int]:
        """Get the News collection ID, fetching and caching it if needed."""
        if self._news_collection_id is not None:
            return self._news_collection_id

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.get(
                    f"{RAINDROP_API_URL}/collections", headers=headers
                ) as response:
                    if not response.ok:
                        return None

                    data = await response.json()
                    collections = data.get("items", [])

                    for collection in collections:
                        if collection.get("title") == NEWS_COLLECTION_NAME:
                            self._news_collection_id = collection.get("_id")
                            return self._news_collection_id

                    return None

            except aiohttp.ClientError:
                return None

    async def save_bookmark(
        self,
        url: str,
        title: Optional[str] = None,
        excerpt: Optional[str] = None,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save a bookmark to Raindrop.io in the News collection."""
        if tags is None:
            tags = []

        # Get the News collection ID
        collection_id = await self.get_news_collection_id()

        request_data = {
            "link": url,
            "pleaseParse": {},
            "tags": tags,
        }

        if title:
            request_data["title"] = title
        if excerpt:
            request_data["excerpt"] = excerpt
        if note:
            request_data["note"] = note
        if collection_id:
            request_data["collection"] = {"$id": collection_id}

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    f"{RAINDROP_API_URL}/raindrop",
                    json=request_data,
                    headers=headers,
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise RaindropApiError(f"API error: {error_text}")

                    data = await response.json()
                    item = data.get("item")
                    if not item:
                        raise RaindropApiError("No item returned from API")

                    return item.get("_id")

            except aiohttp.ClientError as e:
                raise RaindropApiError(f"Request failed: {e}")
