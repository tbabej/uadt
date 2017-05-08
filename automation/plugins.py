from logger import LoggerMixin


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        super(PluginMount, cls).__init__(name, bases, attrs)

        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)


class PluginBase(LoggerMixin):
    """
    Provides common functionality for plugin base classes. Each plugin base,
    however, must furthermore specify the PluginMount metaclass.
    """

    @property
    def plugins(self):
        """
        Returns a dictionary of plugins available.
        """

        return {
            plugin_class.identifier: plugin_class
            for plugin_class in self.plugins
        }

    def get_plugin(self, identifier):
        """
        Returns a plugin class corresponding to the given identifier.
        """

        try:
            return self.plugins[identifier]
        except KeyError:
            self.error('Plugin "{0}" is not available'.format(identifier))
