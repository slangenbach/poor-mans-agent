"""Agent CLI."""

import argparse

from .config import get_config
from .errors import PoorMansAgentError
from .logger import get_logger
from .main import Agent
from .tools import read_url, search

config = get_config()
logger = get_logger(__name__)


def main():
    """Execute Agent from CLI."""
    parser = argparse.ArgumentParser(
        description="A poor man's AI agent",
        epilog="Despite being poorly implemented, this agent can search the web and read the content of URls. Give it a try 8-)",  # noqa: E501
    )
    parser.add_argument("prompt", help="Prompt to pass to the agent")
    args = parser.parse_args()

    agent = Agent(tools=[search, read_url])

    try:
        response = agent.run(args.prompt)
        print(response)
    except PoorMansAgentError as err:
        logger.error("Could not run agent: %s", err)


if __name__ == "__main__":
    main()
