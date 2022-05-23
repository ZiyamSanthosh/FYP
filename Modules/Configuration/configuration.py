import yaml
import os
import main
from yaml.loader import SafeLoader
from requests.exceptions import ConnectionError
from Modules.Constants import constants
from Modules.Logs import logger
from Modules.MetricsManagers.prometheus_monitor import check_prometheus_server_endpoint
from Modules.Forecasters.workload_forecaster import load_forecasting_model


def _load_config() -> dict:
    """
    Load configurations from 'scaler_config.yaml' file into a dictionary

    Returns
    ----------
    dict
        A dictionary object with configuration details
    """

    try:

        with open(constants.PATH_TO_SCALER_CONFIG_FILE) as file:

            data = yaml.load(file, Loader=SafeLoader)
            return data

    except FileNotFoundError as err:
        logger.log_action("error", err.strerror)


def _load_service_account():
    """
    Load service account as environment variable
    """

    try:

        service_account_path = \
            constants.PATH_TO_SERVICE_ACCOUNT_CONFIG + main.configs[constants.SERVICE_ACCOUNT_FILE_NAME]

        with open(service_account_path) as file:

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path

    except FileNotFoundError as err:
        logger.log_action("error", err.strerror)


def _check_service_account_file_availability():
    """
    Check availability of service account file and load.
    """

    if os.path.exists(constants.PATH_TO_SERVICE_ACCOUNT_CONFIG + main.configs[constants.SERVICE_ACCOUNT_FILE_NAME]):
        _load_service_account()
        logger.log_action("info", "Service account file found in the directory and loaded successfully!")
    else:
        logger.log_action("error", "Service account file not found in the directory!", cloud_log_bool=False)
        main.stop_program()


def _check_configuration_file_availability():
    """
    Check availability of configuration file and load.
    """

    if os.path.exists(constants.PATH_TO_SCALER_CONFIG_FILE):

        logger.log_action("info", "Configuration file found in the directory!", cloud_log_bool=False)
        main.configs = _load_config()

        _check_service_account_file_availability()

        if type(main.configs) == dict:
            logger.log_action("info", "Autoscaler configuration file loaded successfully!")
        else:
            logger.log_action("error", "Failed to load the configuration file")
            main.stop_program()
    else:
        logger.log_action("error", "Configuration file not found in the directory!", cloud_log_bool=False)
        main.stop_program(cloud_log_bool=False)


def _check_forecasting_model_availability():
    """
    Check availability of forecasting model file and load.
    """

    if os.path.exists(constants.PATH_TO_DEEP_LEARNING_MODEL):

        logger.log_action("info", "Deep learning model found in the directory!")
        main.forecasting_model = load_forecasting_model()

        if main.forecasting_model.model_created:
            logger.log_action("info", "Forecasting model loaded successfully!")
        else:
            logger.log_action("error", "Failed to load the forecasting model")
            main.stop_program()

    else:
        logger.log_action("error", "Deep learning model not found in the directory!")
        main.stop_program()


def _check_prometheus_availability():
    """
    Initial method to check the availability of the prometheus metric server.
    """

    try:
        prom = check_prometheus_server_endpoint(main.configs)
        if prom.check_prometheus_connection() and prom.url == main.configs[constants.PROMETHEUS_SERVER_ADDRESS]:
            logger.log_action("info", "Prometheus server connected successfully in endpoint " + prom.url)

    except ConnectionError:
        logger.log_action("error", "Failed to access prometheus server endpoint")
        main.stop_program()


def _check_cloud_monitoring_dashboard_status():
    """
    Check status of cloud metric publishing and cloud logging.
    """

    if not main.configs[constants.ENABLE_CLOUD_LOGGING]:
        logger.log_action("info", "Cloud logging disabled", cloud_log_bool=False)
    else:
        logger.log_action("info", "Cloud logging enabled")

    if not main.configs[constants.ENABLE_CLOUD_METRIC_PUBLISHING]:
        logger.log_action("info", "Cloud metric publishing disabled", cloud_log_bool=False)
    else:
        logger.log_action("info", "Cloud metric publishing enabled")


def load_fundamentals():
    """
    Method to cross validate the existence of all needful files.
    """

    _check_configuration_file_availability()
    _check_forecasting_model_availability()
    _check_prometheus_availability()
    _check_cloud_monitoring_dashboard_status()

    logger.log_action("info", "Waiting for a fresh minute...")
