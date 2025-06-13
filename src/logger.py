import logging
import sys


def setup_logger(name=""):
    # Create a logger instance
    logger = logging.getLogger(name)

    # Set the log level to INFO or higher
    logger.setLevel(logging.INFO)

    # Create a stream handler to log to stdout
    stream_handler = logging.StreamHandler(sys.stdout)

    # Set the log level for the stream handler to INFO or higher
    stream_handler.setLevel(logging.INFO)

    # Create a formatter to define the log message format
    formatter = logging.Formatter(
        "%(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    )

    # Set the formatter for the stream handler
    stream_handler.setFormatter(formatter)

    # Add the stream handler to the logger
    logger.addHandler(stream_handler)

    # Return the logger instance
    return logger