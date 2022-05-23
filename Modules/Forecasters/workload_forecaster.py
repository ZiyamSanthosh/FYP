from darts import TimeSeries
from darts.models import TCNModel
from darts.dataprocessing.transformers import Scaler
from darts.models.forecasting.torch_forecasting_model import TorchForecastingModel
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from Modules.Logs import logger

from Modules.Constants import constants


def load_forecasting_model() -> TorchForecastingModel:
    """
    Load the forecasting model

    Returns
    -------
    TCNModel
        Temporal Convolutional Network forecasting model.
    """

    return TCNModel.load_model(constants.PATH_TO_DEEP_LEARNING_MODEL)


def _scale_time_series(time_series: TimeSeries, scaler: Scaler) -> TimeSeries:
    """
    Method to scale time series of requests per minute

    Parameters
    ----------
    time_series
        TimeSeries object with the data of requests per minute for the last 10 minutes.
    scaler
        Scaler object to scale timeseries

    Returns
    -------
    TimeSeries
        Scaled timeseries.
    """

    series_transformed = scaler.fit_transform(time_series)
    return series_transformed


def _inverse_scale_prediction(prediction: TimeSeries, scaler: Scaler) -> TimeSeries:
    """
    Method to reverse scale the predicted resultant timeseries

    Parameters
    ----------
    prediction
        Predicted results using the provided time series (number of requests for the next minute)
    scaler
        Same scaler object used to scale and transform the input timeseries

    Returns
    -------
    TimeSeries
        inverse scaled timeseries.
    """

    return scaler.inverse_transform(prediction)


def _create_covariate_series(transformed_time_series: TimeSeries) -> TimeSeries:
    """
    Method to scale time series of minute covariate series

    Parameters
    ----------
    transformed_time_series
        scaled time series of requests per minute

    Returns
    -------
    TimeSeries
        Scaled minute covariate series.
    """

    past_covariate_series = datetime_attribute_timeseries(
        transformed_time_series, attribute='minute', one_hot=True
    )
    covariate_scaler = Scaler()
    scaled_covariate_series = covariate_scaler.fit_transform(past_covariate_series)
    return scaled_covariate_series


def forecast_future_workload(time_series: TimeSeries, model: TCNModel, configuration: dict) -> int:
    """
    Method for forecasting the future workload (number of requests) for the next minute.

    Parameters
    ----------
    time_series
        TimeSeries object with the data of requests per minute for the last 10 minutes.
    model
        Deep learning based forecasting model for forecasting purposes.
    configuration
        configurations passed for the custom HPA programme

    Returns
    -------
    int
        Number of requests to be expected for the next minute.
    """

    scaler = Scaler()
    transformed_time_series = _scale_time_series(time_series, scaler)
    past_covariate_series = _create_covariate_series(transformed_time_series)

    prediction = model.predict(
        n=1,
        series=transformed_time_series,
        past_covariates=past_covariate_series,
    )
    prediction_result = _inverse_scale_prediction(prediction, scaler)

    if int(time_series.values()[8][0]) <= int(time_series.values()[9][0]):

        final_prediction = int(
            int(round(float(prediction_result.data_array().data)))
            * (1 + configuration[constants.PREDICTION_ERROR_MITIGATION_VALUE])
        )
        logger.log_action("info", "Forecasted workload for the next minute is: " + str(final_prediction))
        return final_prediction

    elif int(time_series.values()[8][0]) > int(time_series.values()[9][0]):

        final_prediction = int(
            int(round(float(prediction_result.data_array().data)))
        )
        logger.log_action("info", "Forecasted workload for the next minute is: " + str(final_prediction))
        return final_prediction
