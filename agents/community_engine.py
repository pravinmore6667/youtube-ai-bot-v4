import asyncio
from typing import Dict, Any, List
from router.ai_router import ask_json
from utils.logger import get_logger

log = get_logger("CommunityEngine")

class CommunityEngine:
    """
    Enterprise Community & Audience Engine
    Handles AI comment replies, audience sentiment analysis, community post generation,
    and audience segmentation.
    """
    def __init__(self):
        self.segments = ["casual_viewers", "hardcore_fans", "skeptics", "new_subscribers"]

    async def analyze_sentiment(self, comments: List[str]) -> Dict[str, Any]:
        """Analyze overall audience sentiment from recent comments."""
        if not comments:
            return {"sentiment": "neutral", "score": 50, "themes": []}

        comments_str = "\n".join(comments[:20])

        prompt = f"""
        Analyze the audience sentiment of these recent YouTube comments.
        Comments:
        {comments_str}

        Return a strict JSON:
        {{
            "overall_sentiment": "positive|neutral|negative",
            "sentiment_score_0_to_100": 85,
            "main_themes": ["theme 1", "theme 2"]
        }}
        """

        try:
            result = await ask_json(prompt, is_fast=True)
            log.info(f"Analyzed sentiment for {len(comments)} comments.")
            return result
        except Exception as e:
            log.warning(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "score": 50, "themes": []}

    async def generate_community_post(self, topic: str, performance_data: Dict[str, Any]) -> str:
        """Generate an engaging YouTube community post to build audience hype."""
        prompt = f"""
        Generate a highly engaging YouTube Community Post to build hype for our upcoming video about: {topic}.
        Consider that our recent videos have had {performance_data.get('views', 'good')} views.
        The post should include a question to spark comments and use appropriate emojis.

        Return strict JSON:
        {{
            "post_text": "The full text of the community post",
            "poll_options": ["Option A", "Option B", "Option C"]
        }}
        """

        try:
            result = await ask_json(prompt, is_fast=True)
            log.success(f"Generated community post for topic: {topic}")
            return result
        except Exception as e:
            log.warning(f"Community post generation failed: {e}")
            return {}

community_engine = CommunityEngine()
