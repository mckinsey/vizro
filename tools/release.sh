# !/usr/bin/env bash

set -eu

GITHUB_USER=$1
GITHUB_REPO=$2
GITHUB_TAGGING_TOKEN=$3
PACKAGE=$4
VERSION=$5
BODY_PATH=$6

GITHUB_ENDPOINT="https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPO}/releases"

BODY=$(jq -Rs . < "$BODY_PATH")

PAYLOAD=$(cat <<-END
{
    "tag_name": "${VERSION}",
    "target_commitish": "main",
    "name": "${PACKAGE}-${VERSION}",
    "body": ${BODY},
    "draft": false,
    "prerelease": false
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
