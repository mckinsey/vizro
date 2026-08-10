import logging
import os
import warnings

__version__ = "0.4.2"

# TODO: I think this collides with the VIZRO_LOG_LEVEL setting, as basicConfig can only be set once
logging.basicConfig(level=os.getenv("VIZRO_AI_LOG_LEVEL", "INFO"))


class VizroAIDeprecationWarning(DeprecationWarning):
    """Warns that the vizro-ai package as a whole is deprecated."""


warnings.warn(
    "vizro-ai is deprecated: 0.4.2 is its final release and no further development or releases are planned. "
    "Use [Vizro-e2e-flow](https://github.com/mckinsey/vizro/tree/main/vizro-e2e-flow/) "
    "or [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/) instead. See "
    "https://github.com/mckinsey/vizro/blob/main/vizro-ai/DEPRECATION.md for details.",
    category=VizroAIDeprecationWarning,
    stacklevel=2,
)
