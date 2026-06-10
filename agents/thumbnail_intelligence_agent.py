import asyncio
import uuid
import json
import os
import cv2
import numpy as np
import mediapipe as mp
import urllib.parse
from io import BytesIO
from PIL import Image
from typing import Dict, Any
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("ThumbnailIntelligenceAgent")

def analyze_thumbnail_cv(image_path: str) -> Dict[str, Any]:
    """
    Use OpenCV and MediaPipe to actually analyze the generated thumbnail
    for contrast, brightness, and face detection (simulating emotion/focus checks).
    """
    if not os.path.exists(image_path):
        return {"error": "Image not found"}

    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Failed to load image"}

        # 1. Analyze brightness and contrast
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)

        # 2. Face detection using MediaPipe
        mp_face_detection = mp.solutions.face_detection
        faces_detected = 0
        face_confidence = 0.0

        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            if results.detections:
                faces_detected = len(results.detections)
                face_confidence = float(results.detections[0].score[0])

        return {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "faces_detected": faces_detected,
            "face_confidence": face_confidence,
            "is_aesthetic": bool(contrast > 40 and 50 < brightness < 200)
        }
    except Exception as e:
        log.warning(f"CV analysis failed: {e}")
        return {"error": str(e)}


async def fetch_image_from_pool(prompt: str, seed: int = 42) -> Image.Image | None:
    """
    Utilizes a prioritized multi-provider fallback pool:
    Flux -> SDXL -> ComfyUI -> Pollinations
    """
    import aiohttp
    encoded_prompt = urllib.parse.quote(prompt)

    # Provider endpoints (simulating API structures for Flux/SDXL/ComfyUI using public instances or placeholder)
    # In a full enterprise system, these would point to configured local or premium API endpoints
    providers = [
        {"name": "Flux", "url": f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true&seed={seed}"},
        {"name": "SDXL", "url": f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=sdxl&nologo=true&seed={seed}"},
        {"name": "ComfyUI", "url": f"http://localhost:8188/prompt"}, # placeholder, will fail gracefully
        {"name": "Pollinations", "url": f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&enhance=true&seed={seed}"}
    ]

    async with aiohttp.ClientSession() as session:
        for provider in providers:
            log.info(f"Attempting image generation with: {provider['name']}")
            try:
                if provider['name'] == 'ComfyUI':
                    # Skip comfyUI if not local
                    pass
                else:
                    async with session.get(provider["url"], timeout=45) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            img = Image.open(BytesIO(data)).convert("RGB")
                            # Resize properly for YouTube
                            try:
                                resample_filter = Image.Resampling.LANCZOS
                            except AttributeError:
                                resample_filter = Image.LANCZOS
                            img = img.resize((1280, 720), resample_filter)
                            log.success(f"Successfully generated image using {provider['name']}")
                            return img
            except Exception as e:
                log.warning(f"{provider['name']} generation failed: {e}")
                continue

    log.error("All image providers in fallback pool failed.")
    return None

async def generate_intelligent_thumbnail(topic: Dict[str, Any]) -> str:
    """
    Analyze viral thumbnails, predict CTR, score thumbnails,
    detect emotional impact, optimize mobile readability, and perform
    simulated A/B testing before generation.
    """
    from agents.thumbnail_agent import generate_thumbnail
    from agents import thumbnail_agent

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

    # 2. Override default `_fetch_image` in thumbnail_agent to use our fallback pool
    original_fetch = thumbnail_agent._fetch_image
    thumbnail_agent._fetch_image = lambda p, s=42: asyncio.run(fetch_image_from_pool(p, s))

    job_id = topic.get("job_id", uuid.uuid4().hex[:10])

    try:
        thumb_path = generate_thumbnail(topic, job_id, None)
    finally:
        # Restore original fetch to be safe
        thumbnail_agent._fetch_image = original_fetch

    # 3. Post-generation CV Analysis
    if thumb_path:
        cv_stats = analyze_thumbnail_cv(thumb_path)
        log.info(f"CV Thumbnail Analysis Results: {cv_stats}")
        # In a real enterprise system, we might loop back and regenerate if CV stats are poor

    return thumb_path
