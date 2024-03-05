import logging
from functools import wraps
from urllib.parse import urlparse

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


def _is_relative_url(url):
    """Checks if the URL is relative.

    Absolute URLs: https://www.google.com, http://www.google.com
    Relative URLs: /first-page, first-page, www.google.com

    """
    parsed_url = urlparse(url)
    return not bool(parsed_url.netloc)


def _clean_url(url, allowed_characters):
    """Cleans the URL and returns it in a format suitable for use as an anchor link.

    Based on how Github generates anchor links - see:
    https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
    """
    url = url.strip().lower().replace(" ", "-")
    url = "".join(character for character in url if character.isalnum() or character in allowed_characters)

    if url.startswith("/"):
        return url
    return "/" + url
