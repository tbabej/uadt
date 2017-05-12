"""
Usage: theater [-v] <scenario>
"""

import importlib
import multiprocessing
import os
import os.path
import shlex
import subprocess
import sys
import time

from docopt import docopt

from uadt.automation.scenario import Scenario
from uadt.logger import LoggerMixin


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

    def initialize_appium(self, appium_ready, scenario_finished):
        env = os.environ.copy()
        env['JAVA_HOME'] = "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-1.b12.fc25.x86_64/"
        env['PATH'] = env['PATH'] + ":/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-1.b12.fc25.x86_64/bin/"
        env['ANDROID_HOME'] = "/home/tbabej/Installed/Android/"

        # Restart ADB server
        adb = os.path.join(env['ANDROID_HOME'], 'platform-tools/adb')
        subprocess.run(['sudo', adb, 'kill-server'])
        subprocess.run(['sudo', adb, 'start-server'])

        process = subprocess.Popen(shlex.split('appium'), env=env)
        time.sleep(5)
        appium_ready.set()
        scenario_finished.wait()
        self.info("Terminating now")
        process.terminate()
        time.sleep(3)

    def main(self):
        arguments = docopt(__doc__, version='theater')
        self.setup_logging(level='debug' if arguments['-v'] else 'info')
        self.import_plugins()

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

        scenario_cls = Scenario.get_plugin(arguments['<scenario>'])
        if scenario_cls is None:
            sys.exit(1)

        scenario = scenario_cls()
        self.info("Executing scenario: {0}".format(scenario.identifier))
        try:
            scenario.execute()
        finally:
            scenario_finished.set()


def main():
    theater = Theater()
    theater.main()

if __name__ == '__main__':
    main()