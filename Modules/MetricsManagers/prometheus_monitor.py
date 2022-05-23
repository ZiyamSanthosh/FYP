import time
import pandas as pd
from typing import Optional, Tuple
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from darts import TimeSeries
from darts.utils.missing_values import fill_missing_values
from datetime import timedelta, datetime
from Modules.Constants import constants
from Modules.Logs import logger


def check_prometheus_server_endpoint(configurations: dict) -> PrometheusConnect:
    """
    check for the connectivity of the prometheus metric server using the provided host address

    Parameters
    ----------
    configurations
        configurations passed for the custom HPA programme

    Returns
    -------
    PrometheusConnect
        A PrometheusConnect object with connection details.
    """

    prom = PrometheusConnect(
        url=configurations[constants.PROMETHEUS_SERVER_ADDRESS],
        disable_ssl=True
    )
    return prom


def getTimeSeries(configurations: dict) -> Optional[Tuple[TimeSeries, int]]:
    """
    Retrieve timeseries data of request count from the prometheus metrics server for the last 10 minutes

    Parameters
    ----------
    configurations
        configurations passed for the custom HPA programme

    Returns
    -------
    TimeSeries
        A TimeSeries of requests per minute.
    int
        Number of requests received in the previous minute from prometheus server
    """

    prom = PrometheusConnect(
        url=configurations[constants.PROMETHEUS_SERVER_ADDRESS],
        disable_ssl=True
    )

    start_time = parse_datetime("9m").replace(second=0, microsecond=0)
    end_time = parse_datetime("now").replace(second=0, microsecond=0)

    logger.log_action(
        "info",
        "Time series to be received for the interval from " +
        time.strftime(constants.DATE_TIME_FORMAT_STRING, time.localtime((start_time - timedelta(minutes=1)).timestamp()))
        + " to " +
        time.strftime(constants.DATE_TIME_FORMAT_STRING, time.localtime((end_time - timedelta(minutes=1)).timestamp()))
    )

    result = prom.custom_query_range(
        query=constants.PROMQL_HAPROXY_REQUEST_COUNT,
        start_time=start_time,
        end_time=end_time,
        step='60'
    )

    if result[0]['metric'] == constants.PROMQL_RESPONSE_METRIC:
        logger.log_action("info", "Response received from Prometheus metric server successfully")

        final_time_series = []

        for item in result[0]['values']:
            current_time = time.strftime(
                constants.DATE_TIME_FORMAT_STRING,
                time.localtime((datetime.fromtimestamp(item[0]) - timedelta(minutes=1)).timestamp())
            )

            final_time_series.insert(
                0,
                {
                    constants.TIME_SERIES_TIME_COLUMN: current_time,
                    constants.TIME_SERIES_VALUE_COLUMN: int(round(float(item[1])))
                }
            )

        dataframe = pd.DataFrame.from_dict(final_time_series)
        dataframe[constants.TIME_SERIES_TIME_COLUMN] = pd.to_datetime(dataframe.time)

        last_minute_request_count = int(dataframe[constants.TIME_SERIES_VALUE_COLUMN].iloc[0])

        series = fill_missing_values(
            TimeSeries.from_dataframe(
                dataframe,
                constants.TIME_SERIES_TIME_COLUMN,
                [constants.TIME_SERIES_VALUE_COLUMN]
            ),
            "auto"
        )

        return series, last_minute_request_count

    else:
        logger.log_action("error", "Error occurred while retrieving response from metric server")
        return None
