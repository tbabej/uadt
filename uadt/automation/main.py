"""
Usage: theater [-v] <scenario>
"""

import importlib
import sys

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

    def main(self):
        arguments = docopt(__doc__, version='theater')
        self.setup_logging(level='debug' if arguments['-v'] else 'info')
        self.import_plugins()

        scenario_cls = Scenario.get_plugin(arguments['<scenario>'])
        if scenario_cls is None:
            sys.exit(1)

        scenario = scenario_cls()
        self.info("Executing scenario: {0}".format(scenario.identifier))
        scenario.execute()


def main():
    theater = Theater()
    theater.main()

if __name__ == '__main__':
    main()
