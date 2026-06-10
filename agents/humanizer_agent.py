import asyncio
from router.ai_router import ask
from utils.logger import get_logger

log = get_logger("HumanizerAgent")

async def humanize_script(script: str) -> str:
    """
    Apply human speech pacing, emotional emphasis, natural pauses,
    imperfect speech rhythm, and storytelling enhancement.
    Avoids robotic outputs for TTS processing.
    """
    if "[Humanized]" in script:
        return script

    prompt = f"""
You are a Humanization Speech Engine for Text-to-Speech (TTS).
Your task is to take the following script and deeply rewrite it to sound indistinguishable from a real human speaking casually but passionately.

Apply these rules strictly to avoid robotic outputs:
1. Insert natural pauses using ellipses (...) or em-dashes (—).
2. Use emotional emphasis through capitalization for words that require punch (e.g., "This is HUGE").
3. Add imperfect speech rhythm by inserting minor filler words appropriately ("well,", "you see,", "look,").
4. Enhance storytelling by making the sentence lengths varied (some short and punchy, some flowing).

Do not output any reasoning or conversational text. Output ONLY the humanized script.

Script to humanize:
{script}
"""
    log.info("Applying human speech pacing and emotional emphasis...")
    try:
        humanized = await ask(prompt, is_fast=False)
        return "[Humanized]\n" + humanized.strip()
    except Exception as e:
        log.warning(f"Humanization optimization failed: {e}")
        return script
