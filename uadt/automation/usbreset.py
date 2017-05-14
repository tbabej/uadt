#!/usr/bin/python3

"""
uadt-reset-usb - Resets the given devname.

Usage:
    uadt-reset-usb <devname>
"""

import os
import subprocess
import fcntl

from docopt import docopt

USBDEVFS_RESET_CODE = 21780

def main():
    arguments = docopt(__doc__)
    devname = arguments['<devname>']

    try:
        with open(devname, 'w', os.O_WRONLY) as f:
            fcntl.ioctl(f, USBDEVFS_RESET_CODE, 0)
        print("Successfully reset device.")
    except (Exception, IOError):
        print("Could not reset the dvice")

if __name__ == '__main__':
    main()
