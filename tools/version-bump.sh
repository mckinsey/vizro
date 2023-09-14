#!/bin/bash

set -eu

GITHUB_USER=$1
GITHUB_REPO=$2
GITHUB_TAGGING_TOKEN=$3
PACKAGE=$4
VERSION=$5
HEAD=$6

GITHUB_ENDPOINT="https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPO}/pulls"

PAYLOAD=$(cat <<-END
{
    "title": "Version bump after ${PACKAGE}-${VERSION}",
    "head": "${HEAD}",
    "base": "main",
    "maintainer_can_modify": true
}
END
)

STATUS=$(curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_TAGGING_TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  ${GITHUB_ENDPOINT} \
  -d "${PAYLOAD}")

echo "${STATUS}"
