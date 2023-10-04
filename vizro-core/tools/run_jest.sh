#!/bin/bash

if node --version >/dev/null 2>&1; then
  echo "Execute the command \"npm install\" to update your node modules to the latest versions..."
  npm install >/dev/null 2>&1;
  echo "Running jest tests."
  npx jest "$@";
else
  echo "
  Node.js is not installed or there was an issue.

  To run tests for the javascript files you need to:
  1. Install Node.js by downloading the LTS version at https://nodejs.org/en/download
  2. Run command: \"npm install\" (to install npm dependencies)
  3. Run command: \"hatch run test-js\" again (to run javascript tests)
  "
fi
