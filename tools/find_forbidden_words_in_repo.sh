#!/bin/bash

# openai.api_base check
api_base_word="openai.api_base"
api_base_finder=$(grep -Irwno --exclude=find_forbidden_words_in_repo.sh --exclude-dir={.git,*cache*,*node_modules*,venv} . -e "$api_base_word")

# If openai.api_base is found
if [[ $api_base_finder ]]; then
  echo "Please remove URL base for development:"
  echo "$api_base_finder"
  exit 1
fi
