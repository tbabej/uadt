import datetime
import contextlib
import os
import random
import re
import subprocess
import shlex
import time
import json

from selenium.common.exceptions import StaleElementReferenceException

from uadt import config, constants
from uadt.plugins import PluginBase, PluginMount
from uadt.automation.generator import DataGenerator
from uadt.automation.driver import ImageRecognitionDriver
from uadt.automation.markov import MarkovChain


class Scenario(PluginBase, metaclass=PluginMount):

    app_package = None  # Must be provided
    app_activity = None  # Must be provided
    new_command_timeout = '50000'
    auto_launch = True
    no_reset = True
    automation_name = "uiautomator2"

    # Override to specify that multiple devices are required for this scenario
    devices = 1

    def __init__(self, appium_ports, phones):
        """
        Initialize the plugin. Create Appium driver instance with required
        capabilities.
        """

        # Verify class attribute requirements
        if self.app_package is None:
            raise ValueError("Package name must be provided.")

        if self.app_activity is None:
            raise ValueError("Startup activity name must be provided.")

        # Storage for events
        self.marks = []

        # Acts like a stack
        self.metadata = []

        # Store for generic metadata, like phone model or its IP
        self.generic_metadata = {}

        # Remember the phone information
        self.phones = phones

        # Store phone related metadata for eternity
        for index, phone in enumerate(self.phones):
            self.add_generic_metadata(
                'phone_{0}_name'.format(index),
                phone['identifier']
            )
            self.add_generic_metadata(
                'phone_{0}_android_ver'.format(index),
                phone['platformVersion']
            )
            self.add_generic_metadata(
                'phone_{0}_model'.format(index),
                phone['model']
            )
            self.add_generic_metadata(
                'phone_{0}_ip'.format(index),
                phone['ip']
            )

        # Determine the file name template
        self.file_identifier = '{plugin}_{timestamp}_{phone}'.format(**{
            'plugin': self.identifier,
            'phone': self.phones[0]['identifier'],
            'timestamp': datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        })

        # Fake data generator
        self.generator = DataGenerator()

        # Create appium instance(s)
        generic_capabilities = {
            'appPackage': self.app_package,
            'appActivity': self.app_activity,
            'newCommandTimeout': self.new_command_timeout,
            'autoLaunch' : self.auto_launch,
            'noReset': self.no_reset,
            'automationName': self.automation_name
        }

        for index, phone in enumerate(self.phones):
             capabilities = generic_capabilities.copy()
             capabilities.update(phone)

             self.debug("Initializing appium interface (phone {})".format(index))

             driver = ImageRecognitionDriver(
                 'http://localhost:{0}/wd/hub'.format(appium_ports[index]),
                 capabilities
             )

             # Configure generous implicit wait time (if manual action is needed)
             driver.implicitly_wait(60)

             # Set the driver attribute for this phone
             # Name convention: 1st phone - self.driver
             #                  2nd phone - self.driver2
             #                  ith phone - self.driveri
             setattr(
                 self,
                 'driver' if index == 0 else 'driver{}'.format(index+1),
                 driver
             )

    def _build_markov_chain(self):
        """
        Inspects all the steps and builds the first order markov chain
        representing the interaction with the application.
        """

        # Find all step methods and extract information out of them
        step_methods_names = [
            method_name
            for method_name in dir(self)
            if method_name.startswith('step_')
        ]

        step_info = [
            self._parse_step_docstring(step)
            for step in step_methods_names
        ]

        # Determine the initial and final state from the class docstring
        initial, final = self._parse_class_docstring()

        self.chain = MarkovChain(step_info, initial=initial, final=final)


    def _parse_step_docstring(self, step_name):
        """
        Parses the docstring of the step method, obtaining all the contained
        metadata (start and end nodes, weight, etc.)
        """

        method = getattr(self, step_name)
        docstring = method.__doc__

        STEP_METADATA_REGEX = re.compile(
            'Start:\s+(?P<start_node>\w+)\s+'
            'End:\s+(?P<end_node>\w+)\s+'
            '(Weight:\s+(?P<weight>[\d\.]+)\s+)?'
        )

        match = STEP_METADATA_REGEX.search(docstring)

        if not match:
            raise ValueError("The step method '{0}' does not"
                "have properly built" "docstring".format(step_name))

        return {
            'name': '_'.join(step_name.split('_')[1:]),
            'start_node': match.group('start_node'),
            'end_node': match.group('end_node'),
            'weight': float(match.group('weight'))
                      if match.group('weight') is not None else 1.0,
        }

    def _parse_class_docstring(self):
        """
        Parses the docstring of the scenario class to determine the initial and
        final state.
        """

        docstring = self.__doc__

        CLASS_METADATA_REGEX = re.compile(
            '\s+Initial:\s+(?P<initial>\w+)\s+'
            '\s+Final:\s+(?P<final>\w+)\s+'
        )

        match = CLASS_METADATA_REGEX.search(docstring)

        if not match:
            raise ValueError("The class docstring is not built properly.")

        return match.group('initial'), match.group('final')

    def steps_by_random_walk(self, length):
        """
        Runs the step methods as determined by the random walk over the
        corresponding markov chain.
        """

        self.debug("Initializing random walk of length '{0}'"
                   .format(length))

        for node_name in self.chain.random_walk(length=length):
            self.debug("Performing step: '{0}'".format(node_name))
            method = getattr(self, 'step_' + node_name)
            method()

    @contextlib.contextmanager
    def capture(self, timeout=5):
        """
        Captures network traffic that passes the network inteface while the
        yielded block of code is executed + while the timeout expires.

        Arguments:
          timeout: the number of seconds we should wait (and capture) after the
                   action has been performed
        """

        # Build the capture query
        # We want to capture all the incoming and outgoing traffic for each
        # mobile device involved
        query_parts = []
        for phone in self.phones:
            query_parts.append('host {0}'.format(phone['ip']))

        query = ' or '.join(query_parts)

        # Start the capture
        filename = os.path.join("data", self.file_identifier + '.pcap')
        args = shlex.split("tshark -l -n -T pdml -i {0} -w {1} '{2}'"
                           .format(config.CAPTURE_INTERFACE, filename, query))

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
                self.error('An exception occurred during the execution of '
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

        # Build the markov chain. This ends up in no-op if no step methods
        # heve been defined.
        self._build_markov_chain()

        # Mark the start point and run the script
        with self.capture():
            self.run()

        # Capture is over, process the marks now
        filename = os.path.join("data", self.file_identifier + '.marks')

        # Build metadata structure
        metadata = {
            'generic': self.generic_metadata,
            'events': self.marks
        }

        with open(filename, 'w') as mark_file:
            mark_file.write(json.dumps(metadata))

    def add_metadata(self, key, value):
        """
        Adds metadata element into the mark dictionary.
        """

        self.debug("Adding metadata {0}='{1}'".format(key, value))
        self.metadata[-1][key] = value

    def add_generic_metadata(self, key, value):
        """
        Adds generic metadata element.
        """

        self.debug("Adding generic metadata {0}='{1}'".format(key, value))
        self.generic_metadata[key] = value

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
        start = datetime.datetime.utcnow()
        yield
        self.debug("Phase out with timeout of {0:.2f} seconds".format(timeout))
        time.sleep(timeout)
        end = datetime.datetime.utcnow()

        # Generate mark data
        mark_data = {
            'name': name,
            'start': start.strftime(constants.MARKS_TIMESTAMP),
            'end': end.strftime(constants.MARKS_TIMESTAMP),
            'timeout': timeout,
        }
        mark_data.update(self.metadata.pop())

        # Save the generated mark data
        self.marks.append(mark_data)

    def find(self, identifier, method=None):
        """
        Finds the element.
        """

        # Perform method detection if needed
        # String starting with / is a XPATH, everything else is an identifier
        if method is None:
           if identifier.startswith('/'):
               method = 'xpath'
           else:
               method = 'identifier'

        # Attempt to find the element using given method
        if method == 'identifier':
            return self.driver.find_element_by_id(identifier)
        elif method == 'xpath':
            return self.driver.find_element_by_xpath(identifier)
        else:
            raise Exception("Unsupported method")

    def click(self, identifier_or_object, retries=5):
        """
        Clicks on the selected element. Transparetnly handles associated
        problems, like StaleObjectException.
        """

        if retries < 0:
            raise Exception("Could not click the element {0}".format(identifier_or_object))

        if isinstance(identifier_or_object, str):
            element = self.find(identifier_or_object)
        else:
            element = identifier_or_object

        try:
            element.click()
        except (StaleElementReferenceException, Exception) as e:
            print(type(e))
            self.click(identifier_or_object, retries=retries-1)
