import schedule
import sys

import main
from darts import TimeSeries
from Modules.Logs import logger
from Modules.Configuration.configuration import load_fundamentals
from Modules.MetricsManagers.prometheus_monitor import getTimeSeries
from Modules.Forecasters.workload_forecaster import forecast_future_workload
from Modules.AdaptionManager.resource_adaptor import scaling_decisions
from Modules.MetricsManagers.cloud_metric_publisher import cloudMetricPublishing

logger.log_action("info", "Custom Autoscaler started running!", cloud_log_bool=False)

configs = None
forecasting_model = None


def stop_program(cloud_log_bool=True):
    """
    Method to stop the execution of the custom HPA programme with relevant logs.

    Parameters
    ----------
    cloud_log_bool
        Boolean to decide whether the log to be added to the cloud or not.
    """
    logger.log_action("info", "Custom autoscaler stopped running successfully!", cloud_log_bool=cloud_log_bool)
    sys.exit()


def main_method():
    """
    Main Method of the system.
    """

    logger.log_action("info", "New iteration triggered")
    time_series, last_minute_request_count_from_prometheus = getTimeSeries(main.configs)

    if type(time_series) == TimeSeries and time_series.n_timesteps == 10:

        logger.log_action("info", "Time series prepared for prediction process!")
        future_workload = forecast_future_workload(time_series, main.forecasting_model, main.configs)
        pod_count = scaling_decisions(future_workload, main.configs)

        try:
            cloudMetricPublishing(pod_count, future_workload, last_minute_request_count_from_prometheus, main.configs)
        except:
            logger.log_action("error", "Error while publishing metrics to cloud. Skipping process for current "
                                       "iteration!")

    elif type(time_series) == TimeSeries and time_series.n_timesteps < 10:

        logger.log_action("error", "Minimum of 10 time steps required for prediction process! Received " + str(
            time_series.n_timesteps) + " only!")

    else:
        logger.log_action("error", "Error while preparing the time series!")

    logger.log_action("info", "Waiting for the next iteration...")


schedule.every().minute.at(":00").do(main_method)

load_fundamentals()

try:
    while True:
        schedule.run_pending()
except KeyboardInterrupt:
    stop_program()
