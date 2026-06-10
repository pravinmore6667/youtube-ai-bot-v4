import asyncio
from typing import Dict, Any
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("AlgorithmAgent")

async def optimize_for_algorithm(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deeply optimize CTR, Retention, Session duration, Replay value,
    Returning viewers, and Subscriber conversion for the YouTube Algorithm.
    """
    if metadata.get("algorithm_optimized"):
        return metadata

    prompt = f"""
You are a YouTube Algorithm Optimization Engine.
Your task is to deeply optimize the metadata to maximize CTR, Session Duration, and Subscriber Conversion.

Current Metadata:
Title: {metadata.get('title')}
Description: {metadata.get('description')}
Tags: {metadata.get('tags')}

Apply these optimizations:
1. Maximize CTR: Keep title under 65 chars, use curiosity/emotional triggers.
2. Maximize Search Ranking: Front-load the primary keyword in the description's first 2 lines.
3. Maximize Conversion: Include a strong call-to-action (CTA) to subscribe near the top of the description.

Return a strict JSON object with the optimized values:
{{
  "title": str,
  "description": str,
  "tags": [str]
}}
"""
    log.info("Applying deep YouTube Algorithm optimizations to metadata...")
    try:
        optimized = await ask_json(prompt, is_fast=True)
        if optimized and "title" in optimized:
            metadata["title"] = optimized["title"]
            metadata["description"] = optimized["description"]
            if isinstance(optimized.get("tags"), list):
                metadata["tags"] = optimized["tags"]
            metadata["algorithm_optimized"] = True
    except Exception as e:
        log.warning(f"Algorithm optimization failed: {e}")
        # If parsing fails, fall back to simple appends
        metadata["algorithm_optimized"] = True
        if "tags" in metadata:
            if isinstance(metadata["tags"], list):
                metadata["tags"].extend(["viral", "trending", "must watch"])

    return metadata
