import asyncio
import re
from router.ai_router import ask
from utils.logger import get_logger

log = get_logger("RetentionAgent")

async def optimize_retention(script: str) -> str:
    """
    Deep Retention Optimization:
    Insert curiosity loops, add pattern interrupts every 20-40 sec,
    detect boring segments, improve pacing dynamically, add emotional
    transitions, and dopamine spikes.
    """
    if "[Optimized for Retention]" in script:
        return script

    prompt = f"""
You are a YouTube Retention Optimization Engine.
Your task is to deeply rewrite the following script to maximize watch time, session duration, and replay value.
Apply the following retention strategies:
1. Insert "curiosity loops" (e.g., teasing a massive reveal for later in the video). Mark them with [Curiosity Loop].
2. Insert "[Pattern Interrupt]" or "[Visual Hook]" markers where pacing slows down (every 20-40 seconds).
3. Enhance emotional transitions between points.
4. Add dopamine spikes (exciting phrasing, high energy words).
5. Remove any boring, generic, or robotic fluff.

Do not output any reasoning or conversational text. Output ONLY the optimized script.

Script to optimize:
{script}
"""
    log.info("Applying deep retention optimization to script...")

    def _force_markers(text: str) -> str:
        # If AI didn't add Pattern Interrupts, force them roughly every ~70 words (approx 30 seconds of speech)
        if "[Pattern Interrupt]" not in text:
            words = text.split()
            if len(words) > 70:
                new_words = []
                for i, w in enumerate(words):
                    new_words.append(w)
                    if i > 0 and i % 70 == 0 and w.endswith((".", "!", "?")):
                        new_words.append("\n\n[Pattern Interrupt]\n\n")
                text = " ".join(new_words)

        # If AI didn't add a Curiosity Loop, add one near the start
        if "[Curiosity Loop]" not in text:
             # Find first paragraph break or first sentence
             match = re.search(r'\n\n|\.\s', text)
             if match:
                 idx = match.end()
                 text = text[:idx] + " [Curiosity Loop] " + text[idx:]

        return text

    try:
        optimized = await ask(prompt, is_fast=False)
        optimized = _force_markers(optimized)
        return "[Optimized for Retention]\n" + optimized.strip()
    except Exception as e:
        log.warning(f"Retention optimization failed, using original script. Error: {e}")
        script = _force_markers(script)
        return "[Optimized for Retention]\n" + script.strip()
