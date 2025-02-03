"""File to store constants."""

from pathlib import Path

import vizro

ALL_OPTION = "ALL"
NONE_OPTION = "NONE"
MODULE_PAGE_404 = "not_found_404"
EMPTY_SPACE_CONST = -1
ON_PAGE_LOAD_ACTION_PREFIX = "on_page_load_action"
FILTER_ACTION_PREFIX = "filter_action"
PARAMETER_ACTION_PREFIX = "parameter_action"
ACCORDION_DEFAULT_TITLE = "SELECT PAGE"
VIZRO_ASSETS_PATH = Path(__file__).with_name("static")
# For dev versions, a branch or tag called e.g. 0.1.20.dev0 does not exist and so won't work with the CDN. We point
# to main instead, but this can be manually overridden to the current feature branch name if required.
# This would only be the case where you need to test something with serve_locally=False and have changed
# assets compared to main. In this case you need to push your assets changes to remote for the CDN to update,
# and it might also be necessary to clear the CDN cache: https://www.jsdelivr.com/tools/purge.
GIT_BRANCH = vizro.__version__ if "dev" not in vizro.__version__ else "main"
BASE_EXTERNAL_URL = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{GIT_BRANCH}/vizro-core/src/vizro/"
