# Poor Man's Agent (PMA)

![CI](https://github.com/slangenbach/poor-mans-agent/actions/workflows/ci.yml/badge.svg)

A lightweight (not to say 'poor') AI agent implementation that can search the web and read website content.

![Logo](assets/logo.png)

## About PMA

This project was inspired by a homework assignment given during the excellent [SolveIt][5] developed by [Answer.AI][6].
It demonstrates how to build a functional agentic AI system using basic components:

- An LLM for reasoning and decision-making
- Simple function calling for tool use
- Web search and URL reading capabilities
- An iterative loop to complete multi-step tasks

The _poor man's_ moniker reflects its minimalist approach, showing that effective AI agents don't require extensive code or complicated architectures.

## Prerequisites

- [uv][1]
- [Task][2]
- Optional: API key for OpenAI-compatible LLM provider (e.g. [OpenRouter][3])
- Optional: API key for [Jina AI][4] to use ready-made tools

## Installation

Make sure you meet the prerequisites

### Using uv

Install the package directly:

```
uv add git+https://github.com/slangenbach/poor-mans-agent.git
```

Or use it without installation:

```
uvx --from git+https://github.com/slangenbach/poor-mans-agent.git pma "Your prompt here"`
```

### Using pip

Install the package:

```
pip install git+https://github.com/slangenbach/poor-mans-agent.git
```

## Configuration

Copy **.env.example** to **.env** in the project root directory and set the following variables:

| Variable | Description | Note |
| --- | --- | --- |
| AI_MODEL_KEY | API key for OpenAI-compatible LLM provider | Required if using a hosted model without a free tier |
| JINA_AI_KEY | API key for Jina AI services | Required for search and URL reading |
| AI_MODEL_BASE_URL | Base URL for LLM API | Defaults to 'https://openrouter.ai/api/v1' |
| AI_MODEL_NAME | Model identifier | Defaults to 'openrouter/mistralai/mistral-small-3.1-24b-instruct:free' |
| TOOL_CALL_TIMEOUT | Timeout for tool calls in seconds | Defaults to 30 |
| LOG_LEVEL | Set the logging level | Defaults to 'INFO' |

## Usage

### CLI

Once installed, you can run the agent from the command line:

```bash
pma "What does it take to build an AI agent in Python?"
```

The agent will:
1. Analyze your prompt
1. Decide which tools to use
1. Execute the necessary steps
1. Return a final answer

Example queries:
- `pma "Find the latest news about AI agents"`
- `pma "Read the content from https://www.answer.ai/posts/2025-10-13-video-to-doc.html and summarize it"`
- `pma "Search for Python tutorials on building AI agents"`

### Programmatically

You can also use the agent in your Python code:

```python
from poor_mans_agent.main import Agent
from poor_mans_agent.tools import search, read_url

agent = Agent(tools=[search, read_url])

response = agent.run("What does it take to build an AI agent in Python?")
print(response)
```

It's also possible to customize the agent:

```python
agent = Agent(
    model="google/gemini-3-flash-preview",  # Use a different model
    tools=[search, read_url],
    system_prompt="You are an expert Gopher. Everything you do is written in Go.",  # Add custom system prompt
    max_iterations=5  # Allow more tool calls
)
```

## Troubleshooting

### "Could not run agent" errors

- **Missing API keys**: Make sure all required environment variables are set in your `.env` file
- **Invalid API keys**: Verify your `AI_MODEL_KEY` and `JINA_AI_KEY` are valid and have sufficient credits
- **Model not found**: Check that `AI_MODEL_NAME` is a valid model identifier for your provider

### "Agent exceeded max iterations" error

The agent stops after 3 tool calls by default. If your task requires more steps:

```python
agent = Agent(tools=[search, read_url], max_iterations=5)
```

### Timeout errors

If tool calls are timing out, increase the timeout in your `.env` file:

```
TOOL_CALL_TIMEOUT=60
```

## Contributing

Check out [CONTRIBUTING.md](CONTRIBUTING.md) for further information.


[1]: https://docs.astral.sh/uv/
[2]: https://taskfile.dev/
[3]: https://openrouter.ai/
[4]: https://jina.ai/
[5]: https://www.answer.ai/posts/2025-10-01-solveit-full.html
[6]: https://www.answer.ai/
