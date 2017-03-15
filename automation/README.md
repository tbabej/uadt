## Automation

The following framework provides a easy way to automate user actions on a
Android (and possibly soon iOS) device in third party apps, while capturing
their network communication.

### Implementation

The implementation leverages [Appium project](https://appium.io), which
provides a feature rich automation broker that controls the device via adb
interface. The broker itself implements an REST API, which we leverage using a
Python library [Appium-Python-Client](https://github.com/appium/python-client).

The capture of the network traffic is done using
[pyshark](https://github.com/KimiNewt/pyshark), which is a wrapper around
Wireshark's CLI interface. The sniffing happens on the machine that runs test
and hence it does not require the device to be rooted (and have tcpdump
installed). In return, the mobile device traffic has to be routed through the
computer (either by shared wifi, or reflected using special network device).

### Setup

To setup the automation, we need to install a few dependencies:
* Android SDK
* Appium framework
* Wireshark

Android SDK can be obtained at: https://developer.android.com/studio/index.html

You need to download the bundle, which contains IDE and necessary android
tools, and follow the setup instructions.

During install you can choose to setup an emulater. This step requires
virtualization capabilities on the computer, and will (currently) create a
virtual Google Nexus 5X device. Please note that for the kind of automation
used in this project a real device is necessary (many messenger apps perform
SMS authentication as part of the sign-up process). Emulator and the real
device are both accessed over the ADB bridge and hence you can switch between
the two transparently.

To communicate with the device we will need the `adb` tool:

    $ sudo dnf install android-tools

To install Appium you need to have `nodejs` (and its npm package manager):

    $ sudo dnf install nodejs npm -y

Then you can obtain Appium simply using npm:

    $ sudo npm install -g appium appium-doctor

The `appium-doctor` package is used to verify the correctness of the
environment setup for Appium.

To run appium, you can use the run_appium.sh script, which will validate your
configuration and if everything looks good, it will launch Appium server:

    $ ./run_appium.sh

However, Appium needs correctly set up `JAVA_HOME` and `ANDROID_HOME`
environment variables. These are sourced from config.sh file:

    $ cp config.sh.in config.sh
    $ vim config.sh  # Setup your own values

Additionally, some Python constants (i.e. interface name) are machine specific
and need to be specified:

    $ cp config.py.in config.py
    $ vim config.py  # Setup your own values
