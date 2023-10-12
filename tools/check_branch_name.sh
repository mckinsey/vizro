#!/bin/sh

BRANCH_LOCAL=$(git symbolic-ref --short HEAD)
BRANCH_CI=${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}
REGEX="^(main|(release|feat|bug|docs|qa|dev|demo|ci|tidy)\/[^/]+(/[^/]+)*)$"

if ! [[ $BRANCH_LOCAL =~ $REGEX ]]  && [[ $BRANCH_CI =~ $REGEX ]]; then
  echo "Branch name is invalid - please rename your branch following this regex syntax: $REGEX"
  exit 1
fi
