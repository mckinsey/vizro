import json
import os

import yaml


def yaml_reader(filepath):
    for file in filepath:
        with open(file, "rb") as f:
            data = yaml.safe_load(f)
            data_str = json.dumps(data)
            if "pull_request_target" in data_str:
                print(f"{file} contains pull_request_target")
                failed_list.append(file)


def failed_list_check(failed_list):
    if failed_list:
        return exit(1)
    else:
        pass


if __name__ == "__main__":
    filepath = os.listdir()
    failed_list = []
    yaml_reader(filepath)
    failed_list_check(failed_list)
