"""
Builds prompts with personality, language, and conversation context.
"""

from typing import List, Tuple, Dict  # noqa: F401


class PromptBuilder:
    PERSONALITIES: Dict[str, str] = {
        "tsundere": "You are tsundere. Act annoyed but helpful.",
        "gentle": "You are gentle and empathetic.",
        "sarcastic": "You are sarcastic but not mean.",
        "professor": "You are a professor, clear and didactic."
    }

    @classmethod
    def build(cls, history: List[Tuple[str, str]], personality: str,
              response_language: str, context_messages: int = 10) -> str:
        if not history:
            return ""
        tone = cls.PERSONALITIES.get(personality, cls.PERSONALITIES["tsundere"])
        lang_inst = f"Respond in {response_language}."
        recent = history[-context_messages:]
        conv = "\n".join(f"User: {u}\nAbigail: {b}" for u, b in recent)
        return (f"{tone}\n{lang_inst}\n\nRecent conversation:\n{conv}\n"
                f"User: {history[-1][0]}\nAbigail:")