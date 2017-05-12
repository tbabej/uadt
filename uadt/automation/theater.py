"""
Usage: theater [-v] [-r <value>] [--phone=<name>...] <scenario>

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

        available_phones = {
            phone['identifier']: phone
            for phone in config.PHONES
        }

        for name in names:
            phone = available_phones.get(name)

            if phone is None:
                raise ValueError("Configuration for phone '{0}' not found.")

            selected.append(phone)

        if not names:
            selected.append(config.PHONES[0])

        return selected

    @staticmethod
    def _local_port_free(port):
        """
        Checks if the given port on localhost is free.
        """

        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with closing(socket) as s:
            return s.connect_ex(('localhost', port)) == 0

    @staticmethod
    def _generate_random_free_port(start, end):
        """
        Generates a random port that is free to use (in the given interval).
        """

        while True:
            port = random.randint(start, end)
            if Theater.local_port_free(port):
                return port

    def initialize_appium(self, appium_ready, scenario_finished):
        env = os.environ.copy()
        env['JAVA_HOME'] = "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-1.b12.fc25.x86_64/"
        env['PATH'] = env['PATH'] + ":/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-1.b12.fc25.x86_64/bin/"
        env['ANDROID_HOME'] = "/home/tbabej/Installed/Android/"

        # Restart ADB server
        adb = os.path.join(env['ANDROID_HOME'], 'platform-tools/adb')
        subprocess.run(['sudo', adb, 'kill-server'])
        subprocess.run(['sudo', adb, 'start-server'])

        # Generate a random port to run the appium
        appium_ports = [
            self._generate_random_free_port(4200, 4300)
            for __ in range(self.devices)
        ]
        bootstrap_ports = [
            self._generate_random_free_port(6500, 6600)
            for __ in range(self.devices)
        ]

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
        for process in appium_processes:
            process.terminate()

    def execute_once(self, scenario_cls):
        appium_ready = multiprocessing.Event()
        scenario_finished = multiprocessing.Event()

        appium = multiprocessing.Process(
            target=self.initialize_appium,
            args=(appium_ready, scenario_finished)
        )
        appium.start()

        appium_ready.wait()
        self.info("Appium is ready!")

        time.sleep(5)

        scenario = scenario_cls()
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

        self.setup_logging(level='debug' if arguments['-v'] else 'info')
        self.import_plugins()

        scenario_cls = Scenario.get_plugin(arguments['<scenario>'])
        if scenario_cls is None:
            sys.exit(1)

        self.devices = 2 if scenario_cls.dual_phone else 1
        phones = self.select_phones(
            arguments['--phone'],
        )

        for __ in range(repeat_count):
            self.execute_once(scenario_cls)


def main():
    theater = Theater()
    theater.main()

if __name__ == '__main__':
    main()
