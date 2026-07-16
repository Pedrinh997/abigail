#!/usr/bin/env python3
"""
ABIGAIL – AI Assistant with Gemini
Entrypoint for the application.
"""

import os
import logging
from dotenv import load_dotenv

from abigail.config import Config
from abigail.persistence import HistoryRepository
from abigail.ai_client import AIProvider
from abigail.ui.interface import UI

# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("abigail.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# ENVIRONMENT – Disable Gradio Analytics
# =============================================================================
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

# =============================================================================
# MAIN
# =============================================================================
def main() -> None:
    """Load configuration, initialize dependencies, and launch the UI."""
    load_dotenv()

    config = Config()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    repo = HistoryRepository()
    models = ["models/gemini-2.5-flash", "models/gemini-3.5-flash", "models/gemini-flash-latest"]
    ai = AIProvider(api_key, models)

    ui = UI(config, repo, ai)
    ui.launch()

if __name__ == "__main__":
    main()