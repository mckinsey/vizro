import shutil

import chromedriver_autoinstaller

# Dash tests use Selenium without Selenium Manager (dash pins older selenium). When
# `chromedriver` is not on PATH — e.g. local dev under CI=1 — install a matching binary.
if shutil.which("chromedriver") is None:
    chromedriver_autoinstaller.install()
