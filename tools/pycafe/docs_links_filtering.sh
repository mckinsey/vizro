# !/usr/bin/env bash

playwright install --with-deps chromium
# grep -hoEr 'https://py.cafe[^])"]*'
# here in the '[]' we're deleting this '^])"'characters at the end of the links and stop reading link after it
# -h: Suppress filenames in the output
# -o: Print only the matched (non-empty) parts of a matching line.
# -E: Use regular expressions.
# -r: Recursively read all files under each directory.
#
# sort -u
# sort links and leave only unique ones
#
# grep -vE '^https://py.cafe/?$'
# grep -vE '^https://py.cafe/docs/apps/vizro/?$'
# grep -vE '^https://py.cafe/logo.png'
# here we're excluding this patterns from the grep
# -v: Invert match
# ^: Anchors the match to the start of the line.
# $: Anchors the match to the end of the line.
# /?: Matches zero or one / after hostname
python ../tools/pycafe/test_pycafe_predefined_links.py \
$(grep -hoEr 'https://py.cafe[^])"]*' \
docs/* | \
sort -u | \
grep -vE '^https://py.cafe/?$' | \
grep -vE '^https://py.cafe/docs/apps/vizro/?$' | \
grep -vE '^https://py.cafe/logo.png')
