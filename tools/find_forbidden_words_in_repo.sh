#!/bin/bash

words=$"colour\|visualisation"
words_finder=$(grep -Irwno --exclude=find_forbidden_words_in_repo.sh --exclude-dir={.git,*cache*} . -e "$words")

if [[ $words_finder ]]
then
  echo "Incorrect spelling for $words:
$words_finder"
  exit 1
else
  echo "No $words found in the repo"
fi
