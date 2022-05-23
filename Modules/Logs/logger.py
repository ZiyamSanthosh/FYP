import logging
import logging.config
from Modules.Logs import cloud_logging
from Modules.Constants import constants
import warnings
import main

warnings.filterwarnings("ignore", ".*does not have many workers.*")

logging.basicConfig(format=constants.LOG_MESSAGE_FORMAT, datefmt=constants.LOG_DATE_FORMAT, level=logging.INFO)

log_types = {
    "info": logging.INFO,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "debug": logging.DEBUG
}


def log_action(log_type: str, message: str, cloud_log_bool: bool = True):
    """
    Method to log messages in both local terminal and cloud

    Parameters
    ----------
    log_type
        Severity level of the log to be added
    message
        Log message body
    cloud_log_bool
        Boolean to decide whether the log to be added to the cloud or not

    """
    logging.log(level=log_types[log_type.lower()], msg=message)
    if cloud_log_bool:
        if main.configs[constants.ENABLE_CLOUD_LOGGING]:
            cloud_logging.log_to_cloud(text=message, severity=log_type.upper())
