import logging
import os

from ._vizro import Vizro

__all__ = ["Vizro"]

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))
