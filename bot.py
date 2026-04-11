import discord
import asyncio
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
REPO_PATH = os.path.expanduser(
    os.getenv("REPO_PATH", "~/git/local-llms/mockup-project")
)
OPENCODE_SERVER = os.getenv("OPENCODE_SERVER", "http://localhost:4096")
MODEL = os.getenv("AGENT_MODEL", "ollama/qwen3-coder:30b")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def post(msg: str):
    ch = client.get_channel(CHANNEL_ID)
    # Discord has 2000 char limit per message
    for chunk in [msg[i : i + 1800] for i in range(0, len(msg), 1800)]:
        await ch.send(f"```\n{chunk}\n```")


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


async def agent_loop(task: str):
    await post(f"Task: {task}\nStarting...")
    await post(f"Working in directory: {REPO_PATH}")

    # Architect pass
    await post("Architect planning...")
    plan = await run_opencode(
        f"You are the Architect agent. Do NOT write any code yet. "
        f"Create a concise numbered plan (max 5 steps) to accomplish this task: {task}. "
        f"Output only the plan, nothing else."
    )
    await post(f"Plan:\n{plan[:1200]}")

    if "[error]" in plan or "[no output]" in plan:
        await post("Architect failed. Check opencode server is running on port 4096.")
        return

    # Executor loop
    for attempt in range(1, 4):
        await post(f"Executor attempt {attempt}/3...")
        result = await run_opencode(
            f"You are the Executor agent. Implement this plan by writing all necessary files to disk:\n"
            f"{plan}\n\n"
            f"Task: {task}\n"
            f"Run any tests that exist after implementing. Report what files you created/modified."
        )
        await post(f"Executor output:\n{result[:1200]}")

        # Let's add a debug step to show what files exist
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

        # Reviewer pass
        await post("Reviewer checking...")
        review = await run_opencode(
            f"You are the Reviewer agent. Check the work just done for this task: {task}\n"
            f"List any files created, run existing tests if any, check for obvious errors.\n"
            f"End your response with either:\n"
            f"VERDICT: PASS\n"
            f"or\n"
            f"VERDICT: FAIL - <reason>"
        )
        await post(f"Review:\n{review[:1200]}")

        if "VERDICT: PASS" in review:
            # Commit
            subprocess.run(["git", "add", "-A"], cwd=REPO_PATH)
            commit = subprocess.run(
                ["git", "commit", "-m", f"agent: {task[:60]}"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True,
            )
            await post(f"Committed.\n{commit.stdout or commit.stderr}")
            return

        await post(f"Reviewer said FAIL on attempt {attempt}. Retrying...")

    await post("Max attempts reached. Check the repo manually.")


@client.event
async def on_ready():
    print(f"Bot ready as {client.user}")
    ch = client.get_channel(CHANNEL_ID)
    if ch:
        await ch.send(
            f"```\nAgent forge online on aigenlab ({MODEL})\nCommands: !build <task> | !status | !ls\n```"
        )


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
        await post(f"Last 5 commits:\n{result.stdout or 'No commits yet'}")

    elif msg.content == "!ls":
        result = subprocess.run(
            ["find", ".", "-not", "-path", "./.git/*", "-type", "f"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
        )
        await post(f"Files in repo:\n{result.stdout[:1000]}")

    elif msg.content == "!help":
        await post(
            "Commands:\n"
            "  !build <task>  — run architect→executor→reviewer loop\n"
            "  !status        — show last 5 git commits\n"
            "  !ls            — list files in repo\n"
            "  !help          — this message"
        )


client.run(TOKEN)
