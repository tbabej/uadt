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
