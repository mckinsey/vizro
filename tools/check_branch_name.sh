#!/bin/sh

BRANCH=$(git symbolic-ref --short HEAD)
REGEX="^(main|(release|feat|bug|docs|qa|dev|demo|ci|tidy)\/[^/]+(/[^/]+)*)$"

if ! [[ $BRANCH =~ $REGEX ]]; then
  echo "Branch name '$BRANCH' is invalid - please rename your branch following this regex syntax: $REGEX"
  exit 1
fi