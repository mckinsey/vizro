import logging
import os

from ._vizro_ai import VizroAI

__all__ = ["VizroAI"]

__version__ = "0.1.0"

logging.basicConfig(level=os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))
