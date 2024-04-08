import logging
import os

from ._vizro import Vizro

__all__ = ["Vizro_test"]

__version__ = "0.1.15.dev0"

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))
