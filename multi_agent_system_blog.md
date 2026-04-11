# Building Multi-Agent Systems with OpenCode: A Comprehensive Guide

## Introduction to the Agent-Forge Concept and Multi-Agent Workflows

The agent-forge concept represents an innovative approach to software development by enabling the creation of autonomous agents that collaborate to solve complex tasks. This multi-agent system leverages OpenCode's capabilities to orchestrate different AI agents working in sequence, each with distinct roles: Architect, Executor, and Reviewer. 

This design pattern demonstrates how AI agents can be combined and orchestrated to create more intelligent, capable systems. The Architect agent plans tasks, the Executor agent implements plans by writing code, and the Reviewer agent validates the work. This workflow provides a robust process for building software that can handle increasingly complex requirements through multi-step, multi-agent collaboration.

## The Problem: Empty Responses from Ollama API Calls

During the initial implementation of the multi-agent system, developers encountered a critical issue where agents were producing empty responses or failing to communicate properly with the Ollama API. This problem manifested in several ways:

1. **Empty output responses**: Agents would return only "[no output]" or empty strings
2. **Communication failures**: The system was unable to properly send requests from Discord bot to OpenCode server
3. **Inconsistent API behavior**: Some calls succeeded while others failed, creating unpredictability in multi-agent workflows

These issues were particularly challenging because debugging was difficult when the agents weren't producing clear error messages. In many cases, the root cause was related to the interaction between the Discord bot and the opencode server, particularly when multiple agent calls needed to maintain state.

## The Solution: Using opencode run --attach with Persistent Server

The solution involved switching from running opencode commands as isolated processes to attaching to a persistent opencode server using the `--attach` flag. This crucial architectural change enabled:

- **Persistent server state**: Multiple opencode calls could share context and state
- **Improved reliability**: Reduced failures due to server initialization or API timeouts
- **Better debugging capabilities**: More consistent error reporting and output
- **Enhanced performance**: Avoided server startup overhead for each command

This approach ensures that the agents communicate through a single, persistent OpenCode server instance rather than creating separate processes, which was causing the inconsistent behavior.

## Step-by-Step Implementation Walkthrough

### 1. Environment Setup
First, developers needed to set up their development environment with necessary dependencies:

```bash
# Install opencode
curl -fsSL https://opencode.ai/install | bash

# Set up a Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install discord.py python-dotenv

# Start the opencode server in persistent mode
opencode run --server --port 4096
```

### 2. Configuration Files (.env)
The `.env` file stores all configuration parameters needed by the system:

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=1492612551836565714
REPO_PATH=~/git/local-llms/mockup-project
OPENCODE_SERVER=http://localhost:4096
AGENT_MODEL=ollama/qwen3-coder:30b
```

### 3. Core Implementation in bot.py

The main implementation in `bot.py` includes:

#### Core Components:
- **discord.Client integration** for interaction
- **run_opencode function** that uses `opencode run --attach` for consistent execution
- **agent_loop function** managing the complete workflow (Architect → Executor → Reviewer)
- **Error handling** for timeouts and communication issues

Here's the key implementation of the `run_opencode` function:

```python
async def run_opencode(prompt: str) -> str:
    """Run one opencode turn attached to the running server."""
    cmd = ["opencode", "run", "--attach", OPENCODE_SERVER, "--model", MODEL, prompt]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=REPO_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "OPENCODE_PERMISSION": '{"allow":["*"]}'},
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode().strip()
        if not output and stderr:
            output = f"[stderr]: {stderr.decode()[:500]}"
        return output or "[no output]"
    except asyncio.TimeoutError:
        return "[timeout after 5 min]"
    except Exception as e:
        return f"[error]: {str(e)}"
```

The key insight is using `--attach` to communicate with a persistent server instead of isolated processes, which resolves the earlier empty response issues.

## Code Examples and Key Components

### The Multi-Agent Workflow:
The system implements a three-stage workflow:
1. **Architect**: Plans the task with a numbered plan
2. **Executor**: Executes the plan by writing files to disk
3. **Reviewer**: Validates the execution and provides a verdict

### Architected Plan Generation:
```python
plan = await run_opencode(
    f"You are the Architect agent. Do NOT write any code yet. "
    f"Create a concise numbered plan (max 5 steps) to accomplish this task: {task}. "
    f"Output only the plan, nothing else."
)
```

### Implementation Execution:
```python
result = await run_opencode(
    f"You are the Executor agent. Implement this plan by writing all necessary files to disk:\n"
    f"{plan}\n\n"
    f"Task: {task}\n"
    f"Run any tests that exist after implementing. Report what files you created/modified."
)
```

### Review and Validation:
```python
review = await run_opencode(
    f"You are the Reviewer agent. Check the work just done for this task: {task}\n"
    f"List any files created, run existing tests if any, check for obvious errors.\n"
    f"End your response with either:\n"
    f"VERDICT: PASS\n"
    f"or\n"
    f"VERDICT: FAIL - <reason>"
)
```

## Troubleshooting and Debugging Techniques

Early development encountered several debugging challenges:

### Common Issues and Solutions:
1. **Empty responses**: Resolved by using `--attach` with persistent server 
2. **Communication failures**: Proper error handling with detailed status reporting
3. **Timeout issues**: Implemented 5-minute timeouts with graceful failure handling
4. **Permission issues**: Set proper OPENCODE_PERMISSION environment variable

### Debugging Workflow:
The system includes built-in debugging capabilities:
- **File listing**: Shows which files exist in repo after execution
- **Status reporting**: Provides detailed status updates at each stage
- **Error logging**: Captures and displays stderr output when available

```python
# Debug function that lists files in the repository
try:
    debug_result = subprocess.run(
        ["find", ".", "-not", "-path", "./.git/*", "-type", "f"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
    )
    await post(f"Files in repo after execution:\n{debug_result.stdout[:500]}")
except Exception as e:
    await post(f"Debug error: {str(e)}")
```

## Setting Up a Working Development Environment

### Prerequisites:
1. Install OpenCode: `curl -fsSL https://opencode.ai/install | bash`
2. Create a Python virtual environment
3. Install dependencies: `pip install discord.py python-dotenv`
4. Set up a Discord bot with appropriate permissions
5. Initialize an opencode server with persistent mode

### Environment Configuration:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install discord.py python-dotenv

# Start the persistent opencode server
opencode run --server --port 4096
```

### Running the Multi-Agent System:
```bash
# In another terminal, execute the Discord bot
python bot.py
```

## The Agent Workflow: Architect → Executor → Reviewer

### Architect Stage:
The Architect agent's role is to break down complex tasks into manageable steps. It creates a clear, numbered plan without writing any code. This ensures that tasks are well-defined and understood before implementation begins.

### Executor Stage:
The Executor agent receives the plan from the Architect and implements it by:
- Creating necessary files
- Writing code to accomplish the task
- Running any existing tests
- Reporting what files were created or modified

### Reviewer Stage:
The Reviewer agent validates the work by:
- Checking the created files for correctness
- Running existing tests
- Providing a pass/fail verdict
- Identifying any obvious errors or problems

This workflow ensures quality control while maintaining an efficient development process.

## Testing with Concrete Examples

### Example Task:
A typical test task might be "create a basic web server that handles GET requests to '/api/data' and returns JSON."

### Execution Process:
1. **Architect** produces a plan like: 
   - 1. Create a main server file
   - 2. Setup basic Express.js framework
   - 3. Define the GET route for /api/data
   - 4. Prepare JSON response structure
   - 5. Test the server endpoint

2. **Executor** implements the plan by:
   - Creating server.js file
   - Writing Express.js code
   - Setting up route handlers
   - Adding JSON response functionality

3. **Reviewer** validates:
   - Checks server.js exists and has valid syntax
   - Verifies the route handler works correctly
   - Confirms return value is valid JSON

### Test Results:
When successful, the system returns:
```
Task: Create basic web server for JSON data endpoint
Starting...
Plan:
1. Create server.js file
2. Setup Express.js framework
3. Define GET route for /api/data
4. Create JSON response structure
5. Test server functionality
...
Committed.
```

## Security Considerations and Best Practices

### Environment Security:
1. **Proper Permissions**: The code sets `OPENCODE_PERMISSION` to allow all operations (`{"allow":["*"]}`)
2. **Repository Isolation**: Each agent operates within a specific repository path
3. **Discord Token Protection**: Bot tokens are stored in `.env` files that are git-ignored

### Code Security:
1. **Input Sanitization**: All user input is sanitized before being passed to agents
2. **Command Execution Safety**: Commands are executed within controlled environments  
3. **Resource Limiting**: Timeouts prevent long-running or malicious code execution

### Operational Security:
1. **Persistent Server Security**: The server should only be accessible from trusted environments
2. **Access Control**: Discord bot should only respond to authorized channels
3. **Logging and Monitoring**: Comprehensive status updates for debugging and verification

## Lessons Learned and Key Takeaways

### Critical Architecture Decisions:
1. **Persistent Server over Isolated Processes**: The switching to `--attach` with a persistent server was crucial for reliability
2. **Separation of Concerns**: Each agent had a specific, well-defined role
3. **Error Handling**: Comprehensive error catching prevented system crashes

### Performance Optimization:
1. **Timeout Management**: 5-minute timeouts balance thoroughness with efficiency
2. **State Persistence**: Shared server state reduces overhead
3. **Chunked Messaging**: Discord messages are broken into 1800-character chunks to avoid limits

### Future Enhancements:
1. **Multi-Threaded Execution**: Parallel execution of different agents
2. **Improved Error Recovery**: More sophisticated retry mechanisms
3. **Advanced Validation**: Integration with linters and testing frameworks
4. **Agent Profiling**: Performance metrics tracking for optimization

## Conclusion

The agent-forge multi-agent system demonstrates how OpenCode can be leveraged to create sophisticated autonomous development workflows. By combining architectural planning, intelligent execution, and rigorous validation through multiple agents, developers can build and maintain complex software systems with reduced manual intervention.

The key insights from this implementation include:
- Using persistent servers with `--attach` for consistent agent communication 
- Clear separation of agent roles for well-defined workflows
- Comprehensive error handling for robust operation
- Effective debugging techniques for troubleshooting agent failures

This system not only demonstrates current capabilities but also provides a foundation for building even more sophisticated multi-agent systems that can tackle increasingly complex development challenges through intelligent collaboration and automation.

Whether you're building AI-powered development tools, automating routine coding tasks, or creating complex software solutions through multi-agent collaboration, the patterns and principles from this agent-forge implementation offer a solid foundation for your own projects using OpenCode.

The integration of Discord for human interaction with the automated system makes it accessible to developers who want to monitor progress, provide new tasks, or intervene when necessary, while the underlying multi-agent workflow ensures that most development tasks can be automated effectively.

The success of this implementation underscores the power of combining:
- Powerful AI models through OpenCode
- Well-defined multi-agent workflows  
- Persistent server architectures for reliability
- Comprehensive error handling and debugging capabilities

This approach provides a scalable, maintainable, and effective way to leverage AI agents for software development automation.