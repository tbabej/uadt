import datetime
import contextlib
import os
import random
import subprocess
import shlex
import time
import json

from appium import webdriver

import config
from generator import DataGenerator
from plugins import PluginBase, PluginMount


class Scenario(PluginBase, metaclass=PluginMount):

    app_package = None  # Must be provided
    app_activity = None  # Must be provided
    new_command_timeout = '50000'
    auto_launch = True
    no_reset = True

    dual_phone = False

    def __init__(self):
        """
        Initialize the plugin. Create Appium driver instance with required
        capabilities.
        """

        if self.app_package is None:
            raise ValueError("Package name must be provided.")

        if self.app_activity is None:
            raise ValueError("Startup activity name must be provided.")

        if len(config.PHONES) < 1:
            raise ValueError("Please configure at least one mobile device in config.py")

        if self.dual_phone and len(config.PHONES) < 2:
            raise ValueError("Scenario requires two mobile devices. Please "
                             "configure at least two mobile devices in config.py")

        generic_capabilities = {
            'appPackage': self.app_package,
            'appActivity': self.app_activity,
            'newCommandTimeout': self.new_command_timeout,
            'autoLaunch' : self.auto_launch,
            'noReset': self.no_reset,
            'automationName': "uiautomator2"
        }

        capabilities = generic_capabilities.copy()
        capabilities.update(config.PHONES[0])

        self.debug("Initializing appium interface")

        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', capabilities)

        # Configure generous implicit wait time (if manual action is needed)
        self.driver.implicitly_wait(60)

        if self.dual_phone:
            capabilities = generic_capabilities.copy()
            capabilities.update(config.PHONES[1])

            self.debug("Initializing second appium interface")
            self.driver2 = webdriver.Remote('http://localhost:4724/wd/hub', capabilities)

            # Configure generous implicit wait time (if manual action is needed)
            self.driver2.implicitly_wait(60)

        self.generator = DataGenerator()

        self.file_identifier = '{plugin_identifier}_{timestamp}'.format(**{
            'plugin_identifier': self.identifier,
            'timestamp': datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        })

        self.marks = []

        # Acts like a stack
        self.metadata = []

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

        self.info("Capturing script '{0}' to file '{1}'".format(
            self.identifier,
            filename
        ))

        with open(os.devnull, 'w') as f:
            p = subprocess.Popen(args, stdout=f, stderr=f)
            try:
                yield
            except Exception:
                # In case any problem occurred during the execution of the
                # scenario, remove associated pcap file
                self.error('An exception occurred during the execution of'
                           'the scenario, removing session PCAP file: {}'
                           .format(filename))
                p.terminate()
                with contextlib.suppress(FileNotFoundError):
                    os.remove(filename)
                raise

            # Sleep so that network communication associated with the last
            # action has time to happen
            time.sleep(timeout)
            p.terminate()

    def execute(self):
        """
        Used to wrap scenario run, performing necessary pre and post actions.
        """

        # Mark the start point and run the script
        with self.capture():
            self.run()

        # Capture is over, process the marks now
        filename = os.path.join("data", self.file_identifier + '.marks')

        with open(filename, 'w') as mark_file:
            mark_file.write(json.dumps(self.marks))

    def add_metadata(self, key, value):
        """
        Adds metadata element into the mark dictionary.
        """

        self.debug("Adding metadata {0}='{1}'".format(key, value))
        self.metadata[-1][key] = value

    @contextlib.contextmanager
    def mark(self, name, timeout=None):
        """
        Marks the event in the marks file.
        Captures:
            - start and end of the interval
            - name of the event marked
            - timeout used
            - any metadata explicitly stored
        """

        self.debug("Processing event: {0}".format(name))

        # Generate the timeout time
        timeout = timeout or (random.randint(2,6) + random.random())

        # Prepare metadata store
        self.metadata.append({})

        # Perform the marked event, capture start/end timestamps
        start = datetime.datetime.now()
        yield
        self.debug("Phase out with timeout of {0:.2f} seconds".format(timeout))
        time.sleep(timeout)
        end = datetime.datetime.now()

        # Generate mark data
        mark_data = {
            'name': name,
            'start': start.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'end': end.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'timeout': timeout,
        }
        mark_data.update(self.metadata.pop())

        # Save the generated mark data
        self.marks.append(mark_data)
