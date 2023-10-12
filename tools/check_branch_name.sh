#!/bin/sh

BRANCH=$(git name-rev --name-only HEAD)
REGEX="^(main|(release|feat|bug|docs|qa|dev|demo|ci|tidy)\/[^/]+(/[^/]+)*)$"


if ! [[ $BRANCH =~ $REGEX ]]; then
  echo "Invalid branch name - please rename your branch following this $REGEX syntax."
  exit 1
fi
