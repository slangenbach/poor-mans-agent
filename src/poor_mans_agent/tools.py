"""Agent tools."""

import httpx

from .config import get_config
from .logger import get_logger

config = get_config()
logger = get_logger(__name__)


def search(query: str) -> str:
    """Search the web for the given query using Jina AI."""
    try:
        response = httpx.get(
            url="https://s.jina.ai/",
            params={"q": query},
            headers={
                "Authorization": f"Bearer {config.jina_ai_key.get_secret_value()}",
                "X-Respond-With": "no-content",
            },
            timeout=config.tool_call_timeout,
        )

        response.raise_for_status()

        return response.text

    except httpx.HTTPError as err:
        logger.error("HTTP error during search: %s", err)
        raise
    except Exception as err:
        logger.error("Unexpected error during search: %s", err)
        raise


def read_url(url: str) -> str:
    """Convert the content of an URL to markdown using Jina AI."""
    try:
        response = httpx.get(
            url=f"https://r.jina.ai/{url}",
            headers={"Authorization": f"Bearer {config.jina_ai_key.get_secret_value()}"},
            timeout=config.tool_call_timeout,
        )
        response.raise_for_status()

        return response.text

    except httpx.HTTPError as err:
        logger.error("HTTP error while reading URL: %s", err)
        raise
    except Exception as err:
        logger.error("Unexpected error while reading URL: %s", err)
        raise
