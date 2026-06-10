import asyncio
from typing import Dict, Any
from router.ai_router import ask
from utils.logger import get_logger

log = get_logger("ShortsAgent")

async def optimize_for_shorts(script: str, video_data: Dict[str, Any]) -> str:
    """
    1-second hook optimization, replay-loop ending, mobile-first editing,
    dynamic subtitles, and fast pacing specifically for short-form content.
    """
    if "[Shorts Hook]" in script:
        return script

    prompt = f"""
You are a Short-Form Content Optimization Engine for TikTok, YouTube Shorts, and Reels.
Your task is to aggressively format and rewrite the given script for maximum retention in under 60 seconds.

Apply these strict formatting markers and rewrites:
1. Create a "1-Second Hook" at the very beginning. Mark it with [1-Second Hook].
2. Optimize pacing for extremely fast delivery. Insert [Fast Pacing: cut every 2s] markers.
3. Enforce dynamic subtitle usage by inserting [Dynamic Subtitles ON].
4. Ensure the video is designed for a vertical screen. Insert [Mobile-First Editing].
5. Modify the ending to loop perfectly back into the hook. Mark it with [Replay Loop Ending].

Do not output conversational text. Output ONLY the optimized script.

Script to optimize:
{script}
"""
    log.info("Applying Shorts specialization formatting...")
    try:
        optimized = await ask(prompt, is_fast=True)
        # Ensure fallback markers are present if AI missed them
        if "[1-Second Hook]" not in optimized:
            optimized = "[1-Second Hook]\n[Dynamic Subtitles ON]\n[Mobile-First Editing]\n" + optimized + "\n[Replay Loop Ending]"
        return optimized
    except Exception as e:
        log.warning(f"Shorts optimization failed: {e}")
        return "[1-Second Hook]\n[Dynamic Subtitles ON]\n[Mobile-First Editing]\n" + script + "\n[Replay Loop Ending]"
