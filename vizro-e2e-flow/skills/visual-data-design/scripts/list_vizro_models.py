"""List all available Vizro models.

Run this script to see all available components in your installed Vizro version.
"""

import logging

import vizro.models as vm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Available Vizro models: %s", vm.__all__)
