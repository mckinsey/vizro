"""Script to run all dashboards in the background in circleci."""

import os

os.system("gunicorn dashboard:app -b 0.0.0.0:5002 -w 3 --timeout 90 &")
