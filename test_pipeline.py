import sys
import logging
from config import Config
from pipeline import run_pipeline

# Fake environment variables to avoid validation errors
Config.GEMINI_API_KEY = "test_key"
Config.GROQ_API_KEY = "test_key"
Config.MISTRAL_API_KEY = "test_key"
Config.GROK_API_KEY = "test_key"

import router.gemini_pool
router.gemini_pool.pool.keys.append(router.gemini_pool.GeminiKey("test_key", 0))

import router.provider_manager
class MockProvider(router.provider_manager.BaseProvider):
    name = "mock"
    tier = 1
    def is_configured(self): return True
    async def generate(self, prompt, is_fast=False, max_tokens=4096):
        return '{"title": "Mock Title", "topic": "Mock Topic", "script": "Mock Script", "format": "explainer", "word_count": 100, "estimated_duration_min": 1, "sections": [{"title": "1", "content": "1"}], "title_variants": ["1", "2"]}'

router.provider_manager.manager.register(MockProvider())

from router.failover_engine import get_ordered_providers
print(f"Ordered providers: {get_ordered_providers()}")

print("Pipeline configured. Skipping execution as it requires auth and real resources, but syntax/import is valid.")
