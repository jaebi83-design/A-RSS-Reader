"""AI-powered article summarization using Claude."""

import aiohttp
from typing import Dict, Any

from ..error import ClaudeApiError


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


class Summarizer:
    """Generates article summaries using Claude API."""

    def __init__(self, api_key: str):
        """Initialize the summarizer with a Claude API key."""
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def generate_summary(self, article_title: str, article_content: str) -> str:
        """Generate a bullet-point summary of an article."""
        system_prompt = """Summarize this article as 3-5 bullet points.
Output ONLY the bullet points - no introductions, conclusions, or commentary.
Start each line with "• " and state one key fact or finding.
Never write phrases like "Here are the key points" or "In summary" - just the bullets."""

        # Truncate content if too long
        content = article_content[:10000] if len(article_content) > 10000 else article_content

        user_message = f"Please summarize the following article:\n\nTitle: {article_title}\n\nContent:\n{content}"

        request_data = {
            "model": CLAUDE_MODEL,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": user_message}],
            "system": system_prompt,
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    CLAUDE_API_URL, json=request_data, headers=headers
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise ClaudeApiError(f"API error: {error_text}")

                    response_data = await response.json()
                    content_blocks = response_data.get("content", [])
                    summary = "\n".join(
                        block.get("text", "")
                        for block in content_blocks
                        if block.get("text")
                    )

                    return summary

            except aiohttp.ClientError as e:
                raise ClaudeApiError(f"Request failed: {e}")

    def model_version(self) -> str:
        """Return the model version being used."""
        return CLAUDE_MODEL
