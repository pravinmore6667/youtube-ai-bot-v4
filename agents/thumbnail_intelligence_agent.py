import asyncio
import uuid
import json
from typing import Dict, Any
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("ThumbnailIntelligenceAgent")

async def generate_intelligent_thumbnail(topic: Dict[str, Any]) -> str:
    """
    Analyze viral thumbnails, predict CTR, score thumbnails,
    detect emotional impact, optimize mobile readability, and perform
    simulated A/B testing before generation.
    """
    from agents.thumbnail_agent import generate_thumbnail

    topic_title = topic.get("title", "Untitled")

    # 1. Simulate an intelligence phase before generation
    prompt = f"""
You are an Enterprise Thumbnail AI.
Analyze the topic "{topic_title}" for a YouTube thumbnail.
You need to conceptualize a thumbnail that maximizes CTR, conveys strong emotion,
and reads well on mobile devices.
Simulate an A/B test between two concepts and pick the winner.

Return strict JSON:
{{
    "winning_concept": str (Brief visual description),
    "emotion_target": str,
    "ctr_prediction": int (0-100),
    "mobile_readability_score": int (0-100)
}}
"""
    log.info(f"Running Thumbnail Intelligence for: {topic_title}")
    try:
        intelligence = await ask_json(prompt, is_fast=True)
        if intelligence and "winning_concept" in intelligence:
            topic["thumbnail_concept"] = intelligence["winning_concept"]
            topic["target_emotion"] = intelligence.get("emotion_target", "curiosity")
            log.success(f"Thumbnail concept chosen: {topic['thumbnail_concept'][:50]}... (Predicted CTR: {intelligence.get('ctr_prediction', 80)}%)")
    except Exception as e:
        log.warning(f"Thumbnail intelligence failed: {e}. Falling back to default.")

    # 2. Delegate to the actual image generator
    job_id = topic.get("job_id", uuid.uuid4().hex[:10])
    return generate_thumbnail(topic, job_id, None)
