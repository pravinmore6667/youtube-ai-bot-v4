"""
utils/gemini.py — Backward-compat shim.
"""
import asyncio
from router.ai_router import ask as async_ask, ask_json as async_ask_json, get_status

def _run_coroutine(coro):
    try:
        loop = asyncio.get_running_loop()
        # If we are already in an event loop (e.g. FastAPI dashboard calls ask)
        # we can't use asyncio.run. We can use create_task but since it's blocking
        # we can use run_coroutine_threadsafe if we had a background loop, or nest_asyncio.
        # But wait! If we are in fastapi, it's an async context. We shouldn't use the sync shim.
        # Actually, FastAPI route handlers can be 'def' which run in threadpools, so asyncio.run might fail
        # if the thread already has a loop. But threadpool threads usually don't have a running loop.
    except RuntimeError:
        pass
    return asyncio.run(coro)

def ask(prompt: str, is_fast: bool = False, max_tokens: int = 4096) -> str:
    return _run_coroutine(async_ask(prompt, is_fast, max_tokens))

def ask_json(prompt: str, is_fast: bool = False, max_tokens: int = 4096, retries: int = 2) -> dict:
    return _run_coroutine(async_ask_json(prompt, is_fast, max_tokens, retries))

__all__ = ["ask", "ask_json", "get_status"]
