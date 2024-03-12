import logging
from functools import wraps

logger = logging.getLogger(__name__)


def _log_call(method):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        # We need to run method before logging so that @_log_call works for __init__.
        return_value = method(self, *args, **kwargs)
        logger.debug("Running %s.%s for model with id %s", self.__class__.__name__, method.__name__, self.id)
        return return_value

    return _wrapper


# Validators for reuse
def _validate_min_length(cls, field):
    if not field:
        raise ValueError("Ensure this value has at least 1 item.")
    return field


# Based on how Github generates anchor links - see:
# https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
def clean_path(path: str, allowed_characters: str) -> str:
    path = path.strip().lower().replace(" ", "-")
    path = "".join(character for character in path if character.isalnum() or character in allowed_characters)
    return "/" + path
