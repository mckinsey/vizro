#!/bin/sh

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REGEX="^(main|(release|feat|bug|docs|qa|dev|demo|ci|tidy)\/[^/]+(/[^/]+)*)$"


if ! [[ $BRANCH =~ $REGEX ]]; then
  echo "Invalid branch name - please rename your branch following this $REGEX syntax."
  exit 1
fi
