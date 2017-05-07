#!/usr/bin/bash
source config.sh

start_appium () {
  APPIUM_PID=`ps a | grep node | grep appium | cut -f1 -d' '`
  if [[ ! -z $APPIUM_PID ]]
  then
    # Appium is hard to terminate
    kill -9 $APPIUM_PID
    sleep 3
    kill -9 $APPIUM_PID
    sleep 3
  fi

  if [[ ! -z `$ANDROID_HOME/platform-tools/adb devices | grep 'no permissions'` ]]
  then
    sudo $ANDROID_HOME/platform-tools/adb kill-server
    sleep 2
    sudo $ANDROID_HOME/platform-tools/adb start-server
    sleep 2
  fi

  if [[ -z `$ANDROID_HOME/platform-tools/adb devices | grep 'device'` ]]
  then
    echo "Unable to get ADB working"
    return
  fi

  # Run appium only if appium-doctor checks pass
  if [[ ! -z `appium-doctor 2>&1 | tee /dev/stderr | grep 'Everything looks good'` ]]
  then
    appium
  fi
}

while true
do
  start_appium
done
