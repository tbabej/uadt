"""
Usage: theater [-v] [-r <value>] [--phone=<name>...] [--adb-reset-freq=<value>] <scenario>

Options:
    -v             Verbose.
    -r <value>     Repeat the execution of the scenario.
    --phone <name> Name of the device used to run the test. Does not need to be specified if only one device is connected.
"""

import contextlib
import importlib
import multiprocessing
import os
import os.path
import random
import re
import shlex
import subprocess
import socket
import sys
import time

from docopt import docopt

from uadt.automation.scenario import Scenario
from uadt.logger import LoggerMixin
from uadt import config


class Theater(LoggerMixin):
    """
    A tool that takes care of executing scenarios and performing necessary
    setup.
    """

    def import_plugins(self):
        """
        Robustly import all available scenario plugins.
        """

        import uadt.automation.scenarios as scenarios

        # pylint: disable=broad-except
        for module in scenarios.__all__:
            try:
                module_id = "{0}.{1}".format('uadt.automation.scenarios', module)
                importlib.import_module(module_id)
                self.debug(module_id + " loaded successfully.")
            except Exception as exc:
                self.warning(
                    "The scenarios.{0} module could not be loaded: {1} "
                    .format(module, str(exc)))
                self.log_exception()

    def select_phones(self, names):
        """
        Selects the phones from the configuration according to the CLI options.
        """

        names = names or []

        if self.devices > 1 and len(names) <= 1:
            raise ValueError("Selected scenario requires two devices, "
                             "in such case you need to specify both.")

        selected = []

        configured_phones = {
            phone['identifier']: phone
            for phone in config.PHONES
        }

        for name in names:
            phone = configured_phones.get(name)

            if phone is None:
                raise ValueError("Configuration for phone '{0}' not found.")

            selected.append(phone)

        if not names:
            selected.append(config.PHONES[0])

        # Update selected phones with the information from the adb
        for phone in selected:
            for available in self.available_devices():
                if phone['deviceName'] == available['model']:
                    phone.update(available)
                    break
            else:
                raise ValueError("Phone '{0}' is not available via ADB."
                                 .format(phone['identifier']))


        for phone in selected:
            phone['ip'] = self._obtain_ip(phone)

        return selected

    def available_devices(self):
        """
        Detect available devices and their parameters using adb devices command.
        """

        result = subprocess.run(
            ['adb', 'devices', '-l'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output = result.stdout.decode('utf-8')

        device_regex = re.compile(
           r'(?P<selector>[^\s]+)\s+'
           r'device\s+'
           r'usb:(?P<usb>[^\s]+)\s+'
           r'product:(?P<product>[^\s]+)\s+'
           r'model:(?P<model>[^\s]+)\s+'
           r'device:(?P<device>[^\s]+)'
        )

        for line in output.splitlines():
            # Skip the filler lines
            match = device_regex.search(line)
            if match:
                yield {
                    'selector': match.group('selector'),
                    'usb': match.group('usb'),
                    'product': match.group('product'),
                    'model': match.group('model'),
                    'device': match.group('device')
                }

    def _obtain_ip(self, phone):
        """
        Gets the IP address of the WLAN interface of the given phone.
        """

        args = [
            'adb',
            '-s', phone['selector'],
            'shell',
            'ip', 'route'
        ]

        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        ip_regex = re.compile(
            r'src (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        )

        for line in result.stdout.decode('utf-8').splitlines():
            match = ip_regex.search(line)
            if match:
                return match.group('ip')

    @staticmethod
    def _local_port_free(port):
        """
        Checks if the given port on localhost is free.
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with contextlib.closing(sock) as s:
            try:
                s.bind(('localhost', port))
                return True
            except socket.error as e:
                # 98 - port already in use
                return e.errno != 98

    @staticmethod
    def _generate_random_free_port(start, end):
        """
        Generates a random port that is free to use (in the given interval).
        """

        while True:
            port = random.randint(start, end)
            if Theater._local_port_free(port):
                return port
            else:
                print("Port {0} not free, trying a different one"
                      .format(port))
                time.sleep(1)

    def initialize_appium(self, appium_ready, scenario_finished, comm_queue, adb_reset=True):
        env = os.environ.copy()
        env['ANDROID_HOME'] = config.ANDROID_HOME
        env['JAVA_HOME'] = config.JAVA_HOME
        env['PATH'] = env['PATH'] + ":" + os.path.join(config.JAVA_HOME, "bin/")

        # Restart ADB server
        if adb_reset:
            adb = os.path.join(env['ANDROID_HOME'], 'platform-tools/adb')
            subprocess.run(['sudo', adb, 'kill-server'])
            subprocess.run(['sudo', adb, 'start-server'])

        # Generate a random port to run the appium
        appium_ports = [
            self._generate_random_free_port(4700, 4800)
            for __ in range(self.devices)
        ]
        bootstrap_ports = [
            self._generate_random_free_port(6500, 6600)
            for __ in range(self.devices)
        ]

        # Send the appium port numbers to the parent process
        comm_queue.put(appium_ports)

        # Initialize all the appium processes
        ports = zip(appium_ports, bootstrap_ports)

        appium_processes = []
        for appium_port, bootstrap_port in ports:
            process = subprocess.Popen(
                ['appium', '-p', str(appium_port), '-bp', str(bootstrap_port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
            appium_processes.append(process)

        time.sleep(5)

        appium_ready.set()
        scenario_finished.wait()

        self.info("Terminating all the Appium processes")

        # Send SIGTERM to the appium processes
        for process in appium_processes:
            process.terminate()

        # Allow time for graceful termination
        time.sleep(3)

        # Time is out, finishing blow with SIGKILL
        for process in appium_processes:
            if process.poll() is None:
                process.kill()

    def execute_once(self, scenario_cls, adb_reset):
        appium_ready = multiprocessing.Event()
        scenario_finished = multiprocessing.Event()
        comm_queue = multiprocessing.Queue()

        appium = multiprocessing.Process(
            target=self.initialize_appium,
            args=(appium_ready, scenario_finished, comm_queue, adb_reset)
        )
        appium.start()

        appium_ready.wait()
        self.info("Appium is ready!")

        appium_ports = comm_queue.get()

        scenario = scenario_cls(appium_ports, self.phones)
        self.info("Executing scenario: {0}".format(scenario.identifier))
        try:
            scenario.execute()
        except Exception as e:
            self.debug(str(e))
        finally:
            scenario_finished.set()

        time.sleep(4)

    def main(self):
        arguments = docopt(__doc__, version='theater')

        repeat_count = int(arguments['-r'] or 1)
        adb_reset_freq = int(arguments['--adb-reset-freq'] or 40)

        self.setup_logging(level='debug' if arguments['-v'] else 'info')
        self.import_plugins()

        scenario_cls = Scenario.get_plugin(arguments['<scenario>'])
        if scenario_cls is None:
            sys.exit(1)

        self.devices = 2 if scenario_cls.dual_phone else 1
        self.phones = self.select_phones(
            arguments['--phone'],
        )

        for run_number in range(repeat_count):
            adb_reset = ((run_number + 1) % adb_reset_freq == 0)
            self.execute_once(scenario_cls, adb_reset)


def main():
    theater = Theater()
    theater.main()

if __name__ == '__main__':
    main()
