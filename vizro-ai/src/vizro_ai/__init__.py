import logging
import os

from dotenv import load_dotenv

load_dotenv()

from ._vizro_ai import VizroAI

__all__ = ["VizroAI"]

__version__ = "0.1.2"

logging.basicConfig(level=os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))
