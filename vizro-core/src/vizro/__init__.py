import plotly.io as pio
import logging
import os

from ._vizro import Vizro
from ._themes import dark, light

__all__ = ["Vizro"]

__version__ = "0.1.20.dev0"

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))

pio.templates["vizro_dark"] = dark
pio.templates["vizro_light"] = light
