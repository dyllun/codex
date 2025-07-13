import os
import itertools
from typing import List, Dict, Any

# Default Gemini keys fallback if GEMINI_API_KEYS env is unset
DEFAULT_GEMINI_KEYS = [
    "AIzaSyC4Wvi3dGfxILk37TRnhON_vcWgZi09ahQ",
    "AIzaSyDb9GBb0v5VU9Qx9eQbbkdOZYjtnRvaJ60",
    "AIzaSyAwS8GQTjCJWjfbGD8G6_WwHIe4cRpEfxI",
    "AIzaSyCjcUwsISnTk8MBUeU0jX2EwKzE-KQOYDY",
    "AIzaSyBh1D_sPGa9d9mX8XfiTF3E4iZKjB8hQ7k",
    "AIzaSyB-4dpI0kAcE3T3Jb4e_NKuvvXy9_HXHcE",
]

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _convert_messages_to_gemini(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Convert OpenAI-style messages to Gemini format."""
    return [{"role": m["role"], "parts": [m["content"]]} for m in messages]


class LLMBackend:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        gemini_env = os.getenv("GEMINI_API_KEYS", "")
        gemini_keys = (
            [k.strip() for k in gemini_env.split(",") if k.strip()]
            if gemini_env
            else DEFAULT_GEMINI_KEYS
        )
        self._gemini_cycle = itertools.cycle(gemini_keys)

    def _ask_openai(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if openai is None:
            raise ImportError("openai package not installed")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=kwargs.get("temperature", 0.5),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        return response

    def _ask_gemini(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if genai is None:
            raise ImportError("google-generativeai package not installed")
        api_key = next(self._gemini_cycle, None)
        if api_key:
            genai.configure(api_key=api_key)
        history = _convert_messages_to_gemini(messages)
        response = genai.chat.Completions.create(
            model="gemini-pro",
            contents=history,
            temperature=kwargs.get("temperature", 0.5),
            max_output_tokens=kwargs.get("max_tokens", 1024),
        )
        return {"choices": [{"message": {"content": response.text}}]}

    def ask_llm(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if self.provider == "gemini":
            return self._ask_gemini(messages, **kwargs)
        return self._ask_openai(messages, **kwargs)
