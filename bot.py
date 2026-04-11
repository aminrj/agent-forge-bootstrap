import discord
import asyncio
import subprocess
import os
from datetime import datetime

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
REPO_PATH = os.path.expanduser("~/git/labs/mcp-attack-labs")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def post(msg: str):
    ch = client.get_channel(CHANNEL_ID)
    await ch.send(f"```\n{msg}\n```")


async def run_agent(role: str, prompt: str, model: str) -> str:
    """Run one OpenCode agent turn, return output."""
    cmd = ["opencode", "run", "--model", f"ollama/{model}", "--print", prompt]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=REPO_PATH,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()


async def agent_loop(task: str):
    await post(f"Task received: {task}\nStarting agent loop...")

    # Architect: plan the work
    await post("Architect thinking...")
    plan = await run_agent(
        "architect",
        f"You are the Architect. Create a concise step-by-step plan to: {task}. "
        f"Output only a numbered list of concrete implementation steps.",
        "qwen3-coder:30b",
    )
    await post(f"Plan:\n{plan[:800]}")

    # Executor: implement
    for attempt in range(1, 4):
        await post(f"Executor working (attempt {attempt}/3)...")
        result = await run_agent(
            "executor",
            f"You are the Executor. Implement this plan in the repository:\n{plan}\n"
            f"Write all code to disk. Run tests if any exist.",
            "qwen3-coder:30b",
        )
        await post(f"Executor done. Running reviewer...")

        # Reviewer: validate
        review = await run_agent(
            "reviewer",
            f"You are the Reviewer. Check the implementation:\n{result[:1000]}\n"
            f"Run any existing tests. Reply with either PASS or FAIL: <reason>.",
            "qwen3-coder:30b",
        )
        await post(f"Review result:\n{review[:400]}")

        if "PASS" in review.upper():
            await post(f"Done in {attempt} attempt(s). Committing...")
            subprocess.run(["git", "add", "-A"], cwd=REPO_PATH)
            subprocess.run(
                ["git", "commit", "-m", f"agent: {task[:60]}"], cwd=REPO_PATH
            )
            await post(f"Committed. Task complete.")
            return

    await post("Max attempts reached. Review the output manually.")


@client.event
async def on_ready():
    await post(f"Agent forge online on aigenlab. Send `!build <task>`")


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    if msg.channel.id != CHANNEL_ID:
        return
    if msg.content.startswith("!build "):
        task = msg.content[7:].strip()
        asyncio.create_task(agent_loop(task))
    elif msg.content == "!status":
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
        )
        await post(f"Last 5 commits:\n{result.stdout}")


client.run(TOKEN)
