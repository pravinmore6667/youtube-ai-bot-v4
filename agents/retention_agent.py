import asyncio
from router.ai_router import ask

async def optimize_retention(script: str) -> str:
    """
    Insert curiosity loops, add pattern interrupts every 20-40 sec,
    detect boring segments, improve pacing dynamically, and add engagement triggers.
    Optimizes scripts for watch time, session duration, and viewer retention.
    """
    if "[Optimized for Retention]" in script:
        return script

    prompt = f"""
You are a YouTube Retention Optimization Engine.
Rewrite the following script to maximize watch time.
1. Insert curiosity loops.
2. Add pattern interrupts where pacing slows.
3. Add engagement triggers (e.g., asking viewers to comment, or teasing an upcoming point).

Do not output any reasoning or conversational text. Output ONLY the optimized script.

Script to optimize:
{script}
"""
    try:
        optimized = await ask(prompt, is_fast=False)
        return "[Optimized for Retention]\n" + optimized.strip()
    except Exception:
        return script
