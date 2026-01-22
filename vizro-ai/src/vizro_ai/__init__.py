import logging
import os

__version__ = "0.4.0.dev0"

# TODO: I think this collides with the VIZRO_LOG_LEVEL setting, as basicConfig can only be set once
logging.basicConfig(level=os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))
