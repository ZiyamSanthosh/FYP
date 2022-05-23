from google.cloud import logging
from Modules.Constants import constants


def log_to_cloud(text: str, severity: str):
    """
    Method to log messages to the Google cloud monitoring dashboard

    Parameters
    ----------
    text
        Message of the log
    severity
        The log's severity level
    """
    logging_client = logging.Client()
    cloud_logger = logging_client.logger(constants.CLOUD_LOGGER_NAME)
    cloud_logger.log_text(text, severity=severity)
