#!/bin/bash

# General words/spelling check
general_words="colour\|visualisation"
general_words_finder=$(grep -Irwno --exclude=find_forbidden_words_in_repo.sh --exclude-dir={.git,*cache*,*node_modules*,venv} . -e "$general_words")

# openai.api_base check
api_base_word="openai.api_base"
api_base_finder=$(grep -Irwno --exclude=find_forbidden_words_in_repo.sh --exclude-dir={.git,*cache*,*node_modules*,venv} . -e "$api_base_word")

# If misspelled words are found
if [[ $general_words_finder ]]; then
  echo "Incorrect spelling for $general_words:"
  echo "$general_words_finder"
fi

# If openai.api_base is found
if [[ $api_base_finder ]]; then
  echo "Please remove URL base for development:"
  echo "$api_base_finder"
fi

# Exit if either condition is true
if [[ $general_words_finder || $api_base_finder ]]; then
  exit 1
fi
