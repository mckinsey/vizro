#!/bin/bash

words=$"colour\|visualisation\|openai.api_base"
words_finder=$(grep -Irwno --exclude=find_forbidden_words_in_repo.sh --exclude-dir={.git,*cache*,*node_modules*,venv} . -e "$words")

if [[ $words_finder ]]
then
  echo "Incorrect spelling or forbidden word for $words:
$words_finder"
  exit 1
else
  echo "No $words found in the repo"
fi
