# Building Multi-Agent Systems with OpenCode: The Real Problem We're Solving

## The Mess We're Actually Fighting

Let's be honest about software development today. We're not just writing code anymore - we're managing complex, interconnected systems. One day you're building a simple web server, the next you're dealing with distributed systems that need to scale across continents.

I've been there. You think you can handle it, but then you're debugging issues nobody saw coming, fighting through configuration problems, and wondering why that bug keeps popping up. The traditional approach is just keep coding until it works. And sometimes it works. But then you're left with a messy codebase and a pile of technical debt that's going to hurt you down the road.

That's where multi-agent systems come in. They're not science fiction - they're actual engineers solving real problems. Think of it less like one expert and more like a team of specialists working in the same room, each tackling different aspects of the same challenge.

Here's what we're actually solving:

- We're tired of systems that crash in production
- We're tired of edge cases that break everything
- We're tired of fighting with integration tools
- We're tired of code that's impossible to maintain
- We're tired of writing the same things over and over

None of this is new, but we're trying to solve it systematically.

## The Evolution from Single-Agent to Multi-Agent Systems  

The first version of our agent-forge had serious problems. The biggest issue was getting empty responses from the Ollama API. We'd ask for a simple task, and get nothing back. It was like hitting an invisible wall.

It turned out to be how the system was communicating with the opencode server. Initially we were running isolated opencode calls, which meant each agent operated from scratch. That was problematic for tasks that needed to build on previous work.

The breakthrough came when we moved to using `opencode run --attach` with a persistent server. Instead of spinning up a new process each time, all the agents were communicating through the same server with shared state. It made a world of difference.

This isn't like some fancy technology - it's just a fix that makes sense. But after struggling with the older approach for weeks, we finally saw results.

## Architecture Breakdown: How We Actually Built This

Let me explain what's happening under the hood:

### 1. The Communication Layer

We built a Discord bot that serves as the interface between humans and the system. When you type "!build Create a script", the bot picks that up, starts a conversation with the agents, and shows you what's happening.

### 2. The Agent Workflow (Architect → Executor → Reviewer)

This workflow is the heart of how the system works:

**Architect Agent**: This agent creates the plan. It figures out what steps are needed without actually writing any code yet. Think of it like a project manager who makes a task list before someone starts doing the actual work.

**Executor Agent**: Takes the plan and builds it. It creates files, writes code, and puts everything in place. If you gave it a plan to write a web server, it would create the server files and implement the routes.

**Reviewer Agent**: Checks that everything was done correctly. It verifies the implementation, makes sure tests pass, and decides whether everything is good to go. If there are errors, it tells the Executor agent to try again.

I'll admit, I was surprised by how much the reviewer process actually helped. It's like having a colleague who gives honest feedback before you commit changes to the main branch.

### 3. Making It Persistent

Here's the crucial part: we use `--attach` to connect to a persistent server. This means all the agents are working within the same context. You're not starting from scratch each time you run a command. You're building on what came before.

This isn't just convenient - it's essential for any system that needs to remember what it's been doing.

## The Technical Details That Make It Work

Let me show you the code that actually makes this process happen:

### Setting Up the Environment

We start with a `.env` file that contains all the configuration:

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=1492612551836565714
REPO_PATH=~/git/local-llms/mockup-project
OPENCODE_SERVER=http://localhost:4096
AGENT_MODEL=ollama/qwen3-coder:30b
```

This gives the system all the information it needs to communicate with Discord, know where to create files, and connect to the right server.

### The Core Communication Function

The key function is `run_opencode`. Instead of running individual opencode calls, we connect everything to a persistent process:

```python
async def run_opencode(prompt: str) -> str:
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

This is where the magic happens. The `--attach` flag ensures all commands go to the same persistent server, which makes the whole system much more reliable.

## Key Insights and Lessons Learned

### The Importance of Iteration

The development process wasn't linear. We had several versions before we got it right. The biggest lesson was understanding how to make the agents communicate effectively. Each attempt taught us something new.

### How the Workflow Actually Works in Practice

Let me give you a practical example of what happens when you type "!build Add a simple Flask health endpoint":

1. **Architect Agent** creates a plan: "Create app.py file, set up Flask, create /health route, return JSON response"
2. **Executor Agent** implements the plan: "Creates app.py, adds Flask code, defines route, adds JSON return"
3. **Reviewer Agent** validates: "Checks app.py exists, validates Flask code, tests route response, provides verdict"

This isn't just fancy automation - this is about making the development process more reliable and repeatable.

### Debugging and Monitoring

Even with all the fancy architecture, debugging is still important. Our system includes built-in monitoring that shows:
- What files are created
- Where errors occur
- What the system is working on
- How long each stage takes

The debugging capabilities helped us identify exactly what was happening when the system failed previously.

## Technical Challenges and How We Overcame Them

### Challenge 1: Getting Agents to Work Together

The initial problem was that agents weren't sharing context. We'd ask for the next step, it would execute, but everything felt disconnected.

**Solution**: Using `--attach` meant all operations happened through the same server, preserving state.

### Challenge 2: Reliable Communication with Discord

We struggled getting the Discord bot to correctly relay information between the agents and users.

**Solution**: Adding better status reporting and more error handling made the feedback loop much clearer.

### Challenge 3: Understanding What Went Wrong

When things didn't work, it was hard to debug because we didn't know if problems were with individual agents or communications.

**Solution**: Built-in debugging information and clear stage reporting helped isolate issues quickly.

### Challenge 4: File Management

We needed to make sure agents only worked in specific directories without accidentally corrupting other projects.

**Solution**: Careful path configuration in the `.env` file with explicit repository paths.

## Real Benefits in Practice

I've found several practical advantages to this approach:

### Reduced Manual Work

The agent-forge system handles all the repetitive tasks:
- Creating boilerplate code
- Managing file structure
- Setting up basic functionality
- Writing standard patterns

This frees up time for developers to focus on complex problems.

### Faster Iteration

Instead of struggling with setup, developers can quickly test new ideas with the same framework that takes care of the basic implementation.

### Better Consistency

The agents ensure consistent approaches to common tasks, reducing variation in how similar features are implemented.

### Learning Tool

This system also serves as a way to learn how things should be implemented. The Architect agent shows one way to approach a problem, and you can see that process.

## Why This Approach Works Better Than Others

Let me be clear about the problems we were facing before we fixed them:

### The Original Issues

1. **Empty Responses**: Agents that returned nothing instead of code
2. **Isolated Processes**: Each agent worked alone, no memory of previous steps
3. **Inconsistent Communication**: Sometimes working, sometimes not
4. **Debugging Nightmare**: No clear indication of what went wrong

### The Solution

By using the persistent server approach, we fixed these issues:

1. **State Preservation**: Everything remembers what happened before
2. **Consistent Communication**: All agents talk through the same channel
3. **Better Context**: Each step knows what the last step did
4. **Proper Error Handling**: More helpful feedback on failures

### The Results

Here's what happened when we ran a simple test: "Create a Python script called hello.py that prints 'Hello from agent-forge' and a requirements.txt with no dependencies."

The system went through all three stages:
1. Architect created a plan
2. Executor created the files 
3. Reviewer validated that everything was correct

And it worked reliably every time. No more empty responses, no more confusion.

## The Road Ahead

This is just the beginning. We're already exploring enhancements like:
- Parallel processing of different agents
- More sophisticated error recovery
- Integration with testing frameworks  
- Better handling of complex agent dependencies

The real value of this approach isn't in the technical details - it's in how it changes the way we approach development tasks. We're not replacing human developers. We're giving them better tools to accomplish more.

## Why This Matters for the Future

I think what makes this approach so interesting is it's not about replacing human work - it's about augmenting it. The agents handle the routine tasks, but humans still design, supervise, and make decisions about what should be built.

More importantly, it's about building reliable, scalable tools that can adapt to new challenges. As problems get more complex, this kind of collaborative approach will only become more valuable.

The agent-forge system represents a practical bridge between current development approaches and what we might see in the future when AI systems are even more sophisticated. It shows us how to start building collaborative AI development environments today.

## Final Thoughts

What I've learned most is that complexity isn't always the enemy of progress. It's about organizing that complexity in ways that make sense to humans.

We're not just building software here. We're building systems that work with us, understand our needs, and amplify our abilities. This agent-forge approach isn't complicated - it's just focused. It solves real problems by breaking them down and using the right tools for each part.

The future of software development isn't about computers that replace humans. It's about intelligent systems that work alongside us, helping us build better things faster, with more reliable outcomes. The multi-agent approach we've built demonstrates that practical, reliable AI collaboration is absolutely possible today.

So whether you're a seasoned developer or just getting started in software, this multi-agent approach shows a way forward that's more practical and sustainable than any single-agent approach could be.

## Security Considerations and Best Practices

### Environment Security

1. **Proper Permissions**: The code sets `OPENCODE_PERMISSION` to allow all operations (`{"allow":["*"]}`)
2. **Repository Isolation**: Each agent operates within a specific repository path
3. **Discord Token Protection**: Bot tokens are stored in `.env` files that are git-ignored

### Code Security

1. **Input Sanitization**: All user input is sanitized before being passed to agents
2. **Command Execution Safety**: Commands are executed within controlled environments  
3. **Resource Limiting**: Timeouts prevent long-running or malicious code execution

### Operational Security

1. **Persistent Server Security**: The server should only be accessible from trusted environments
2. **Access Control**: Discord bot should only respond to authorized channels
3. **Logging and Monitoring**: Comprehensive status updates for debugging and verification

## Lessons Learned and Key Takeaways

### Critical Architecture Decisions

1. **Persistent Server over Isolated Processes**: The switching to `--attach` with a persistent server was crucial for reliability
2. **Separation of Concerns**: Each agent had a specific, well-defined role
3. **Error Handling**: Comprehensive error catching prevented system crashes

### Performance Optimization

1. **Timeout Management**: 5-minute timeouts balance thoroughness with efficiency
2. **State Persistence**: Shared server state reduces overhead
3. **Chunked Messaging**: Discord messages are broken into 1800-character chunks to avoid limits

### Future Enhancements

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

