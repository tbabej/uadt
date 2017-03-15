#!/usr/bin/bash
source config.sh

# Run appium only if appium-doctor checks pass
if [[ ! -z `appium-doctor 2>&1 | tee /dev/stderr | grep 'Everything looks good'` ]]
then
  appium
fi
