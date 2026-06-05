import asyncio
import json
from typing import Dict, Any
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("ViewerPsychologyEngine")

async def optimize_script_psychology(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the script and optimizes it based on viewer psychology principles:
    - Curiosity loop generation
    - Dopamine pacing analysis
    - Emotional transition optimization
    - Boredom prediction
    - Replay optimization
    - Attention recovery triggers
    - Retention spike placement
    """
    log.info("Running Viewer Psychology Engine to optimize script...")

    text = script_data.get("full_narration", "")
    if not text:
        log.warning("No script text provided to ViewerPsychologyEngine.")
        return script_data

    prompt = f"""
You are an Advanced Viewer Psychology Engine for a highly successful YouTube channel.
Your job is to take the following script and optimize it for maximum viewer retention, addiction, and emotional engagement.

Analyze and apply the following principles:
1. Curiosity loop generation: Open loops early and close them later.
2. Dopamine pacing: Ensure high-energy moments are spaced correctly.
3. Emotional transition optimization: Move seamlessly between different emotions.
4. Boredom prediction & Attention recovery: Insert pattern interrupts or hooks where viewers typically drop off.
5. Replay optimization: Add subtle details or fast-paced sections that encourage rewatching.
6. Retention spike placement: Add high-value visual or audio cues.

Original Script:
\"\"\"{text[:3000]}\"\"\"

Return a valid JSON object with the optimized script and analysis.
Strictly match this schema:
{{
    "optimized_narration": "The fully optimized script text",
    "curiosity_loops_added": ["loop 1", "loop 2"],
    "attention_recovery_triggers_placed": ["trigger 1", "trigger 2"],
    "pacing_notes": "Notes on how the dopamine pacing was adjusted",
    "boredom_prediction_fixes": "Notes on where boredom was predicted and how it was fixed"
}}
"""

    try:
        result = await ask_json(prompt, is_fast=False)
        if result and "optimized_narration" in result:
            script_data["full_narration"] = result["optimized_narration"]
            script_data["psychology_analysis"] = {
                "curiosity_loops": result.get("curiosity_loops_added", []),
                "attention_recovery": result.get("attention_recovery_triggers_placed", []),
                "pacing_notes": result.get("pacing_notes", ""),
                "boredom_fixes": result.get("boredom_prediction_fixes", "")
            }
            log.success(f"Viewer psychology optimization complete.")
        else:
            log.warning("Viewer psychology optimization failed: Invalid JSON structure.")
    except Exception as e:
        log.warning(f"Viewer psychology optimization failed: {e}")

    return script_data
