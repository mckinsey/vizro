import os

import chromedriver_autoinstaller

# Install chromedriver locally; CI already has it.
if not os.getenv("CI"):
    chromedriver_autoinstaller.install()
