import sys
import logging
import traceback


class LoggerMixin(object):
    """
    This mixin adds logging capabilities to the class. All clases inheriting
    from this mixin use the 'main' logger unless overriden otherwise.

    LoggerMixin also provides convenient shortcut methods for logging.
    """

    logger = logging.getLogger('main')

    # Logging-related helpers
    @classmethod
    def log(cls, log_func, message, *args):
        log_func("{0}: {1}".format(cls.__name__, message), *args)

    # Interface to be leveraged by the class
    @classmethod
    def debug(cls, message, *args):
        cls.log(cls.logger.debug, message, *args)

    @classmethod
    def info(cls, message, *args):
        cls.log(cls.logger.info, message, *args)

    @classmethod
    def warning(cls, message, *args):
        cls.log(cls.logger.warning, message, *args)

    @classmethod
    def error(cls, message, *args):
        cls.log(cls.logger.error, message, *args)

    @classmethod
    def critical(cls, message, *args):
        cls.log(cls.logger.critical, message, *args)

    @classmethod
    def log_exception(cls, exception_type=None, value=None, trace=None):
        if exception_type is None:
            exception_type, value, trace = sys.exc_info()

        cls.error("Exception: %s", exception_type)
        cls.error("Value: %s", value)
        cls.error("Traceback (on a new line):\n%s",
                   "\n".join(traceback.format_tb(trace)))

    # Logging setup related methods
    @classmethod
    def setup_logging(cls, level='info'):
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

        logging_level = level_map.get(level)

        # Setup main logger
        cls.logger.setLevel(logging.DEBUG)

        # Define logging format
        formatter = logging.Formatter('%(levelname)s: %(message)s')

        # Define default handlers
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging_level)
        stream_handler.setFormatter(formatter)

        cls.logger.addHandler(stream_handler)
