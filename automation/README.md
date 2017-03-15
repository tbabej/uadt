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
