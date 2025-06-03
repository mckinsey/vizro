import logging
import os

from dotenv import load_dotenv

load_dotenv()

from ._vizro_ai import VizroAI

__all__ = ["VizroAI"]

__version__ = "0.3.7"

# TODO: I think this collides with the VIZRO_LOG_LEVEL setting, as basicConfig can only be set once
logging.basicConfig(level=os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))
