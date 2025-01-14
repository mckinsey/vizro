"""Script to run all dashboards in the background in circleci."""

import os

import e2e_constants as cnst

os.system(f"gunicorn dashboard:app -b 0.0.0.0:{cnst.DEFAULT_PORT} -w 3 --timeout 90 &")
