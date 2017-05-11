from logger import LoggerMixin


class PluginMount(type):
    """
    Provides common functionality for plugin base classes.
    """

    def __init__(cls, name, bases, attrs):
        super(PluginMount, cls).__init__(name, bases, attrs)

        if not hasattr(cls, '_plugins'):
            cls._plugins = []
        else:
            cls._plugins.append(cls)

    @property
    def plugins(cls):
        """
        Returns a dictionary of plugins available.
        """

        return {
            plugin_class.identifier: plugin_class
            for plugin_class in cls._plugins
        }


class PluginBase(LoggerMixin):
    """
    Provides common functionality for plugin base classes. Each PluginBase
    class still needs to specify PluginMount metaclass.
    """

    @classmethod
    def get_plugin(cls, identifier):
        """
        Returns a plugin class corresponding to the given identifier.
        """

        try:
            return cls.plugins[identifier]
        except KeyError:
            cls.error('Plugin "{0}" is not available'.format(identifier))
