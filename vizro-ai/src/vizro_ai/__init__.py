import logging
import os

__version__ = "0.4.2.dev0"

logger = logging.getLogger("vizro_ai")
logger.setLevel(os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))
