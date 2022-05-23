import time

import google.api_core.exceptions
from google.api import label_pb2 as ga_label
from google.api import metric_pb2 as ga_metric
from google.cloud import monitoring_v3
from Modules.Logs import logger
from Modules.Constants import constants


def _createMetricDescriptor(configurations, metric):
    """
    Create metric descriptor object for new custom metric.

    Parameters
    ----------
    configurations
        Configuration passed for the custom HPA programme.
    metric
        name of the metric

    Returns
    ----------
    MetricDescriptor
        Google MetricDescriptor object.
    """

    client = monitoring_v3.MetricServiceClient()
    descriptor = ga_metric.MetricDescriptor()

    if metric == constants.PREDICTED_REQUEST_COUNT:

        descriptor.type = constants.PREDICTED_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE
        descriptor.description = "This is a custom metric for " + constants.PREDICTED_REQUEST_COUNT

    elif metric == constants.POD_REPLICA_COUNT_BY_DEPLOYMENT:

        descriptor.type = constants.POD_REPLICA_COUNT_BY_DEPLOYMENT_METRIC_DESCRIPTOR_TYPE
        descriptor.description = "This is a custom metric for " + constants.POD_REPLICA_COUNT_BY_DEPLOYMENT
        label2 = ga_label.LabelDescriptor()
        label2.key = "namespace"
        label2.value_type = ga_label.LabelDescriptor.ValueType.STRING
        label2.description = "This is a namespace label"
        descriptor.labels.append(label2)

    elif metric == constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT:

        descriptor.type = constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE
        descriptor.description = "This is a custom metric for " + constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT

    descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE
    descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64

    label1 = ga_label.LabelDescriptor()
    label1.key = "deployment"
    label1.value_type = ga_label.LabelDescriptor.ValueType.STRING
    label1.description = "This is a deployment label"
    descriptor.labels.append(label1)

    label3 = ga_label.LabelDescriptor()
    label3.key = "projectId"
    label3.value_type = ga_label.LabelDescriptor.ValueType.STRING
    label3.description = "This is a projectId label"
    descriptor.labels.append(label3)

    project_id = configurations[constants.PROJECT_ID]
    project_name = f"projects/{project_id}"

    descriptor = client.create_metric_descriptor(
        name=project_name,
        metric_descriptor=descriptor
    )

    logger.log_action("info", "Metric descriptor " + descriptor.name + " created!")

    return descriptor


def _getMetricDescriptor(configurations: dict, metric: str):
    """
    Retrieve metric descriptor of the given metric.

    Parameters
    ----------
    configurations
        Configuration passed for the custom HPA programme.
    metric
        name of the metric

    Returns
    ----------
    MetricDescriptor
        Google MetricDescriptor object.
    """

    client = monitoring_v3.MetricServiceClient()
    project_id = configurations[constants.PROJECT_ID]
    project_name = f"projects/{project_id}"
    descriptor = None
    descriptor_type = None

    if metric == constants.PREDICTED_REQUEST_COUNT:
        descriptor_type = project_name + "/metricDescriptors/" + constants.PREDICTED_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE

    elif metric == constants.POD_REPLICA_COUNT_BY_DEPLOYMENT:
        descriptor_type = project_name + "/metricDescriptors/" + constants.POD_REPLICA_COUNT_BY_DEPLOYMENT_METRIC_DESCRIPTOR_TYPE

    elif metric == constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT:
        descriptor_type = project_name + "/metricDescriptors/" + constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE

    try:
        descriptor = client.get_metric_descriptor(name=descriptor_type)
    except google.api_core.exceptions.NotFound:
        logger.log_action("error", "Metric Descriptor not found! Creating new descriptor...")
        descriptor = _createMetricDescriptor(configurations, metric)
    return descriptor


def _createTimeSeriesPointsForPods(value: int) -> monitoring_v3.Point:
    """
    Creating timeseries point for determined number of pod replicas.

    Parameters
    ----------
    value
        Number of pod replicas.

    Returns
    ----------
    monitoring_v3.Point
        Timeseries point object.
    """

    time_sec = int(time.time())
    end_time = {"seconds": time_sec}
    interval = monitoring_v3.TimeInterval(
        {"end_time": end_time}
    )
    point = monitoring_v3.Point(
        {
            "interval": interval,
            "value": {"int64_value": value}
        }
    )
    return point


def _createTimeSeriesPointsForRequest(value: int) -> monitoring_v3.Point:
    """
    Creating timeseries point for predicted requests count metric.

    Parameters
    ----------
    value
        Number of request count.

    Returns
    ----------
    monitoring_v3.Point
        Timeseries point object.
    """

    current_time = time.localtime(int(time.time()))
    tup = (
        current_time.tm_year,
        current_time.tm_mon,
        current_time.tm_mday,
        current_time.tm_hour,
        current_time.tm_min,
        0,
        current_time.tm_wday,
        current_time.tm_yday,
        current_time.tm_isdst
    )
    time_sec = time.mktime(tup)
    end_time = {"seconds": int(time_sec)}
    interval = monitoring_v3.TimeInterval(
        {"end_time": end_time}
    )
    point = monitoring_v3.Point(
        {
            "interval": interval,
            "value": {"int64_value": value}
        }
    )
    return point


def _createTImeSeriesPointsForPrometheusMetric(value: int) -> monitoring_v3.Point:
    """
    Creating timeseries point for requests count metric from prometheus server.

    Parameters
    ----------
    value
        Number of request count.

    Returns
    ----------
    monitoring_v3.Point
        Timeseries point object.
    """

    current_time = time.localtime(int(time.time()))
    tup = (
        current_time.tm_year,
        current_time.tm_mon,
        current_time.tm_mday,
        current_time.tm_hour,
        current_time.tm_min - 1,
        0,
        current_time.tm_wday,
        current_time.tm_yday,
        current_time.tm_isdst
    )
    time_sec = time.mktime(tup)
    end_time = {"seconds": int(time_sec)}
    interval = monitoring_v3.TimeInterval(
        {"end_time": end_time}
    )
    point = monitoring_v3.Point(
        {
            "interval": interval,
            "value": {"int64_value": value}
        }
    )
    return point


def _publish_predicted_request_count_metric(predicted_workload: int, configurations: dict):
    """
    Method to publish metrics of the predicted request count to the Google cloud monitoring Dashboard

    Parameters
    ----------
    predicted_workload
        Predicted workload for the next minute.
    configurations
        Configuration passed for the custom HPA programme
    """

    descriptor = _getMetricDescriptor(configurations, constants.PREDICTED_REQUEST_COUNT)

    series = monitoring_v3.TimeSeries()
    series.metric.type = descriptor.type
    series.resource.type = "global"

    series.metric.labels["deployment"] = configurations[constants.DEPLOYMENT_NAME]
    series.metric.labels["projectId"] = configurations[constants.PROJECT_ID]

    series.points = [_createTimeSeriesPointsForRequest(predicted_workload)]

    client = monitoring_v3.MetricServiceClient()
    project_id = configurations[constants.PROJECT_ID]
    project_name = f"projects/{project_id}"

    client.create_time_series(
        name=project_name,
        time_series=[series]
    )


def _publish_pod_replica_count_metrics(pod_count_after_scaling: int, configurations: dict):
    """
    Method to publish metrics of the predicted pod replica count to the Google cloud monitoring Dashboard

    Parameters
    ----------
    pod_count_after_scaling
        Number of pod replicas
    configurations
        Configuration passed for the custom HPA programme
    """

    descriptor = _getMetricDescriptor(configurations, constants.POD_REPLICA_COUNT_BY_DEPLOYMENT)

    series = monitoring_v3.TimeSeries()
    series.metric.type = descriptor.type
    series.resource.type = "global"

    series.metric.labels["deployment"] = configurations[constants.DEPLOYMENT_NAME]
    series.metric.labels["projectId"] = configurations[constants.PROJECT_ID]
    series.metric.labels["namespace"] = configurations[constants.NAMESPACE]

    series.points = [_createTimeSeriesPointsForPods(pod_count_after_scaling)]

    client = monitoring_v3.MetricServiceClient()
    project_id = configurations[constants.PROJECT_ID]
    project_name = f"projects/{project_id}"
    client.create_time_series(
        name=project_name,
        time_series=[series]
    )


def _publish_prometheus_server_metric_for_request_count(request_count: int, configurations: dict):
    """
    Method to publish metrics of request count from prometheus metric server to the Google cloud monitoring Dashboard

    Parameters
    ----------
    request_count
        Predicted workload for the next minute.
    configurations
        Configuration passed for the custom HPA programme
    """

    descriptor = _getMetricDescriptor(configurations, constants.PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT)

    series = monitoring_v3.TimeSeries()
    series.metric.type = descriptor.type
    series.resource.type = "global"

    series.metric.labels["deployment"] = configurations[constants.DEPLOYMENT_NAME]
    series.metric.labels["projectId"] = configurations[constants.PROJECT_ID]

    series.points = [_createTImeSeriesPointsForPrometheusMetric(request_count)]

    client = monitoring_v3.MetricServiceClient()
    project_id = configurations[constants.PROJECT_ID]
    project_name = f"projects/{project_id}"

    client.create_time_series(
        name=project_name,
        time_series=[series]
    )


def cloudMetricPublishing(pod_count: int, predicted_workload: int, prometheus_request_count: int, configurations: dict):
    """
    Method to publish custom metrics to the Google cloud monitoring dashboard

    Parameters
    ----------
    pod_count
        Number of pod replicas to be executed for the next iteration
    predicted_workload
        Predicted number of requests for the next minute
    prometheus_request_count
        Number of requests received from prometheus server for the previous minute
    configurations
        Configuration passed for the custom HPA programme
    """

    _publish_pod_replica_count_metrics(pod_count, configurations)
    _publish_predicted_request_count_metric(predicted_workload, configurations)
    _publish_prometheus_server_metric_for_request_count(prometheus_request_count, configurations)
