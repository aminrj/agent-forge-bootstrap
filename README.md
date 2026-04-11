# Agent-Forge: Multi-Agent System for Software Development

This repository demonstrates how to build and use multi-agent systems with OpenCode to automate software development tasks through collaboration between specialized AI agents.

## Overview

Agent-Forge is a proof-of-concept multi-agent system that leverages OpenCode's capabilities to create autonomous development workflows. The system uses three specialized agents working together:

1. **Architect Agent**: Breaks down complex tasks into manageable steps
2. **Executor Agent**: Implements the plan by creating files and writing code  
3. **Reviewer Agent**: Validates the work and provides pass/fail verdict

## Key Features

- **Persistent Server Communication**: Uses `opencode run --attach` for reliable agent communication
- **Discord Integration**: Human interaction through a Discord bot interface
- **Error Handling**: Comprehensive debugging and error reporting
- **Security**: Controlled permissions and repository isolation

## Getting Started

### Prerequisites

1. Install OpenCode: `curl -fsSL https://opencode.ai/install | bash`
2. Python 3.8+
3. Discord bot with appropriate permissions

### Setup

1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install discord.py python-dotenv
   ```

3. Start the persistent OpenCode server:
   ```bash
   opencode run --server --port 4096
   ```

4. Set up your `.env` file with:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_CHANNEL_ID=1492612551836565714
   REPO_PATH=~/git/local-llms/mockup-project
   OPENCODE_SERVER=http://localhost:4096
   AGENT_MODEL=ollama/qwen3-coder:30b
   ```

5. Run the Discord bot:
   ```bash
   python bot.py
   ```

## Usage

Once the bot is running, you can interact with it through Discord:

```
!build Create a Python script that prints "Hello from agent-forge"
```

The system will:
1. Use the Architect agent to create a plan
2. Have the Executor agent implement the plan
3. Run the Reviewer agent to validate the results

## How It Works

The system leverages persistent server communication via `--attach` flag to maintain state between agent interactions. This ensures agents can properly collaborate and share context, which was the key breakthrough that solved the empty response issues with the Ollama API.

## Security

The system includes several security measures:
- Repository isolation to prevent unauthorized file access
- Controlled permissions via OPENCODE_PERMISSION environment variable
- Discord bot token protection in .env files
- Input sanitization and command execution safety

## Architecture

The agent workflow follows a three-stage process:
1. **Architect Stage**: Creates a plan with numbered steps
2. **Executor Stage**: Implements the plan by writing files
3. **Reviewer Stage**: Validates implementation and provides verdict

## Contributing

This is a proof-of-concept demonstration. Contributions are welcome to improve the system's capabilities, add more sophisticated agents, or expand the integration capabilities.

## License

This project is licensed under the MIT License.