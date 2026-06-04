import asyncio
import json
from typing import Dict, Any
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("ViralIntelligenceAgent")

async def analyze_viral_potential(topic: str, script: str) -> Dict[str, Any]:
    """
    Predict viral potential, analyze trending competitors implicitly,
    score CTR probability, score emotional engagement, replay value,
    and retention. Calculate trend momentum.
    """
    prompt = f"""
You are a highly advanced YouTube Viral Prediction Engine.
Your task is to deeply analyze the following video topic and script outline and predict its viral potential.
You must factor in:
- Viral probability
- Trend momentum
- Competition density
- Emotional impact
- Replay probability
- CTR probability

Topic: {topic}
Script snippet (or empty): {script[:1000]}

You must return a valid JSON object strictly matching this schema:
{{
  "viral_score": int (0-100),
  "ctr_score": int (0-100),
  "retention_score": int (0-100),
  "emotional_impact_score": int (0-100),
  "trend_momentum": str ("High", "Medium", "Low"),
  "competition_density": str ("High", "Medium", "Low"),
  "analysis_notes": str
}}
"""
    log.info(f"Analyzing viral potential for topic: {topic[:50]}")
    try:
        result = await ask_json(prompt, is_fast=True)
        if result and "viral_score" in result:
            log.success(f"Viral score generated: {result.get('viral_score')}/100")
            return result
    except Exception as e:
        log.warning(f"Failed to generate viral analysis: {e}")

    # Safe fallback if parsing fails
    return {
        "viral_score": 85,
        "ctr_score": 90,
        "retention_score": 88,
        "emotional_impact_score": 92,
        "trend_momentum": "High",
        "competition_density": "Medium",
        "analysis_notes": "Fallback due to AI parse error. High baseline assumed."
    }
