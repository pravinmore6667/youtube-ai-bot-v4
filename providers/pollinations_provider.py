import aiohttp
from config import config
from router.provider_manager import BaseProvider, manager

class PollinationsProvider(BaseProvider):
    name = "pollinations"
    tier = 3
    timeout = 30

    def is_configured(self) -> bool:
        return True

    async def generate(self, prompt: str, is_fast: bool = False, max_tokens: int = 4096) -> str:
        url = "https://text.pollinations.ai/openai"
        payload = {
            "model": "mistral" if is_fast else "searchgpt",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.35,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    text = await resp.text()
                    raise RuntimeError(f"Pollinations error {resp.status}: {text}")

manager.register(PollinationsProvider())
