import datetime
import contextlib
import os
import subprocess
import shlex
import time

from appium import webdriver

import config
from logger import LoggerMixin

class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        super(PluginMount, cls).__init__(name, bases, attrs)

        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)


class Plugin(LoggerMixin):

    __metaclass__ = PluginMount

    platform_name = 'Android'
    platform_version = '7.1'
    device_name = 'Nexus 5X'
    app_package = None  # Must be provided
    app_activity = None  # Must be provided
    new_command_timeout = '50000'
    auto_launch = True
    no_reset = True

    def __init__(self):
        """
        Initialize the plugin. Create Appium driver instance with required
        capabilities.
        """

        if self.app_package is None:
            raise ValueError("Package name must be provided.")

        if self.app_activity is None:
            raise ValueError("Startup activity name must be provided.")

        capabilities = {
            'platformName': self.platform_name,
            'platformVersion': self.platform_version,
            'deviceName': self.device_name,
            'appPackage': self.app_package,
            'appActivity': self.app_activity,
            'newCommandTimeout': self.new_command_timeout,
            'autoLaunch' : self.auto_launch,
            'noReset': self.no_reset,
        }

        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', capabilities)

        # Configure generous implicit wait time (if manual action is needed)
        self.driver.implicitly_wait(60)

        self.file_identifier = '{plugin_identifier}_{timestamp}'.format(**{
            'plugin_identifier': self.identifier,
            'timestamp': datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        })

        self.marks = []

    @contextlib.contextmanager
    def capture(self, timeout=5):
        """
        Captures network traffic that passes the network inteface while the
        yielded block of code is executed + while the timeout expires.

        Arguments:
          timeout: the number of seconds we should wait (and capture) after the
                   action has been performed
        """

        filename = os.path.join("data", self.file_identifier + '.pcap')
        args = shlex.split("tshark -l -n -T pdml -i {0} -w {1}"
                           .format(config.CAPTURE_INTERFACE, filename))

        self.debug("Capturing script '{0}' to file '{1}'".format(
            self.identifier,
            filename
        ))

        with open(os.devnull, 'w') as f:
            p = subprocess.Popen(args, stdout=f, stderr=f)
            yield
            # Sleep so that network communication associated with the given
            # action has time to happen
            time.sleep(timeout)
            p.terminate()

    def execute(self):
        """
        Used to wrap scenario run, performing necessary pre and post actions.
        """

        filename = os.path.join("data", self.file_identifier + '.marks')

        with open(filename, 'w') as mark_file:

            # Mark the start point and run the script
            with self.capture():
                start_point = datetime.datetime.now()
                self.run()

            # Capture is over, process the marks now
            mark_file.writelines([
                '{time} [{shift}]: {name}\n'.format(**{
                    'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'shift': (time - start_point).total_seconds(),
                    'name': name,
                    })
                for name, time in self.marks
            ])

    def _record_mark(self, name):
        """
        Marks the current event name in the mark list with the current
        timestamp.

        Perform as little as possible to make sure the timestamp is as precise
        as it gets. Processing happens after all data has been captured.
        """

        self.marks.append((name, datetime.datetime.now()))

    @contextlib.contextmanager
    def mark(self, name, timeout=5):
        """
        Marks the timestamp of the event in the mark file.
        """

        self._record_mark('start_{0}'.format(name))
        yield
        time.sleep(timeout)
        self._record_mark('end_{0}'.format(name))
