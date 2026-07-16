"""
Gemini API client with model fallback.
"""

import logging
from typing import List, Tuple, Optional  # noqa: F401
from google import genai

logger = logging.getLogger(__name__)


class AIProvider:
    def __init__(self, api_key: str, models: List[str]) -> None:
        self.api_key = api_key
        self.models = models
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str) -> Tuple[Optional[str], str]:
        for model_name in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response.text and response.text.strip():
                    return response.text, ""
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
        return None, "All models failed"