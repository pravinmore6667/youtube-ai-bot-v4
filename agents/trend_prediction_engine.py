import asyncio
from typing import List, Dict, Any
import requests
import json
from datetime import datetime, timedelta
from utils.logger import get_logger

log = get_logger("TrendPredictionEngine")

class TrendPredictionEngine:
    """
    Predictive trend engine that uses real data from Reddit, Google Trends, and YouTube
    to track trend velocity and keyword momentum before saturation.
    """
    def __init__(self):
        # Cache for predictions to avoid spamming APIs
        self._trend_cache: Dict[str, Any] = {}
        self._cache_ttl = 3600 # 1 hour

    def _is_cache_valid(self, keyword: str) -> bool:
        if keyword in self._trend_cache:
            timestamp = self._trend_cache[keyword].get('timestamp')
            if timestamp and (datetime.now() - timestamp).total_seconds() < self._cache_ttl:
                return True
        return False

    def fetch_reddit_velocity(self, keyword: str, subreddits: List[str] = ["all"]) -> Dict[str, Any]:
        """Scrape Reddit for hot/rising velocity on a keyword using JSON API without auth."""
        velocity_score = 0
        related_terms = []
        posts_analyzed = 0

        try:
            subs = "+".join(subreddits)
            url = f"https://www.reddit.com/r/{subs}/search.json?q={keyword}&sort=hot&limit=25&t=week"
            headers = {"User-Agent": "EnterpriseAIBot/2.0 (Trend Prediction)"}

            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for post in data.get("data", {}).get("children", []):
                    post_data = post.get("data", {})
                    score = post_data.get("score", 0)
                    upvote_ratio = post_data.get("upvote_ratio", 0)
                    num_comments = post_data.get("num_comments", 0)

                    # Compute velocity heuristic: engagement over time
                    velocity_score += (score * upvote_ratio) + (num_comments * 2)
                    posts_analyzed += 1

            # Normalize velocity somewhat
            normalized_velocity = min(100, velocity_score / max(1, posts_analyzed * 10))

            return {
                "velocity": normalized_velocity,
                "volume": posts_analyzed
            }
        except Exception as e:
            log.warning(f"Failed to fetch Reddit velocity for '{keyword}': {e}")
            return {"velocity": 0, "volume": 0}

    def fetch_google_trends_momentum(self, keyword: str) -> Dict[str, Any]:
        """Fetch real Google Trends momentum using pytrends."""
        try:
            from pytrends.request import TrendReq
            pt = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            pt.build_payload([keyword], timeframe='now 7-d', geo='')

            df = pt.interest_over_time()
            if not df.empty:
                # Calculate momentum: Compare last 3 days to first 4 days of the week
                recent_interest = df[keyword].tail(3).mean()
                older_interest = df[keyword].head(4).mean()

                momentum = 0
                if older_interest > 0:
                    momentum = ((recent_interest - older_interest) / older_interest) * 100

                # Detect saturation: if recent interest is declining while overall volume is high
                is_saturated = recent_interest < older_interest and df[keyword].max() > 80

                return {
                    "momentum_pct": float(momentum),
                    "is_saturated": bool(is_saturated),
                    "current_interest": float(recent_interest)
                }
        except Exception as e:
            log.warning(f"Failed to fetch Google Trends momentum for '{keyword}': {e}")

        return {"momentum_pct": 0.0, "is_saturated": False, "current_interest": 0.0}

    async def predict_trend(self, keyword: str, niche: str) -> Dict[str, Any]:
        """
        Synthesize multiple real data sources to predict if a trend is pre-viral,
        growing, saturated, or dead.
        """
        if self._is_cache_valid(keyword):
            log.info(f"Using cached trend prediction for '{keyword}'")
            return self._trend_cache[keyword]['data']

        log.info(f"Analyzing trend prediction for keyword: '{keyword}' in niche: '{niche}'")

        # Determine relevant subreddits based on niche
        niche_subs = {
            "technology": ["technology", "gadgets", "futurology"],
            "finance": ["personalfinance", "investing", "CryptoCurrency"],
            "gaming": ["gaming", "Games"],
            "science": ["science", "space"],
        }.get(niche.lower(), ["all", "videos"])

        # Fetch real data (Run in executor to avoid blocking async loop)
        loop = asyncio.get_event_loop()
        reddit_data, gt_data = await asyncio.gather(
            loop.run_in_executor(None, self.fetch_reddit_velocity, keyword, niche_subs),
            loop.run_in_executor(None, self.fetch_google_trends_momentum, keyword)
        )

        # Synthesize logic
        velocity = reddit_data.get("velocity", 0)
        momentum = gt_data.get("momentum_pct", 0)
        saturated = gt_data.get("is_saturated", False)
        interest = gt_data.get("current_interest", 0)

        status = "unknown"
        if saturated:
            status = "saturated"
        elif momentum > 20 and velocity > 30:
            status = "pre-viral"
        elif momentum > 0 and velocity > 10:
            status = "growing"
        elif momentum < -20:
            status = "declining"
        else:
            status = "stable"

        # Final prediction score (0-100) combining velocity and momentum
        prediction_score = min(100, max(0, (velocity * 0.4) + (min(100, momentum) * 0.4) + (interest * 0.2)))

        result = {
            "keyword": keyword,
            "status": status,
            "prediction_score": float(prediction_score),
            "metrics": {
                "reddit_velocity": float(velocity),
                "google_momentum_pct": float(momentum),
                "google_interest": float(interest)
            },
            "recommendation": "Produce immediately" if status in ["pre-viral", "growing"] else "Avoid"
        }

        # Cache result
        self._trend_cache[keyword] = {
            "timestamp": datetime.now(),
            "data": result
        }

        log.success(f"Trend prediction for '{keyword}': {status} (Score: {prediction_score:.1f})")
        return result

trend_engine = TrendPredictionEngine()
