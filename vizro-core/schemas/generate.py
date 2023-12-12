"""Script to generate JSON schema. For more information, run `hatch run schema --help`."""
import argparse
import json
import sys
from pathlib import Path

from vizro import __version__
from vizro.models import Dashboard

parser = argparse.ArgumentParser(description="Generate JSON schema.")
parser.add_argument("--check", help="check schema is up to date", action="store_true")
args = parser.parse_args()

# TODO: need to setup alias function to keep lowercase if wanted
schema_json = Dashboard.schema_json(indent=4, by_alias=False)
schema_path = Path(__file__).with_name(f"{__version__}.json")

if args.check:
    if json.loads(schema_path.read_text()) != json.loads(schema_json):
        sys.exit("JSON schema is out of date. Run `hatch run schema` to update it.")
    print("JSON schema is up to date.")  # noqa: T201
else:
    schema_path.write_text(schema_json)
