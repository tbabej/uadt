import datetime
import contextlib
import subprocess
import shlex
import os

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
    def capture(self, name):
        filename = '{plugin_identifier}_{name}_{timestamp}.pcap'.format({
            'plugin_identifier': self.identifier,
            'name': name,
            'timestamp': datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        })

        args = shlex.split("tshark -l -n -T pdml -i wlp4s0 -w {0}".format(filename))

        with open(os.devnull, 'w') as f:
            p = subprocess.Popen(args, stdout=f, stderr=f)
            yield
            p.terminate()
