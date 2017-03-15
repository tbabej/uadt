import datetime
import contextlib
import os
import subprocess
import shlex
import time

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

    @contextlib.contextmanager
    def capture(self, name, timeout=5):
        """
        Captures network traffic that passes the network inteface while the
        yielded block of code is executed + while the timeout expires.

        Arguments:
          name: specify the name of the event, used to identify output file
          timeout: the number of seconds we should wait (and capture) after the
                   action has been performed
        """

        filename = '{plugin_identifier}_{name}_{timestamp}.pcap'.format(**{
            'plugin_identifier': self.identifier,
            'name': name,
            'timestamp': datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        })
        filename = os.path.join("data", filename)

        args = shlex.split("tshark -l -n -T pdml -i {0} -w {1}"
                           .format(config.CAPTURE_INTERFACE, filename))

        self.debug("Capturing event '{0}' to file '{1}'".format(name, filename))

        with open(os.devnull, 'w') as f:
            p = subprocess.Popen(args, stdout=f, stderr=f)
            yield
            # Sleep so that network communication associated with the given
            # action has time to happen
            time.sleep(timeout)
            p.terminate()
