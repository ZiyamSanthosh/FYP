# configs
PROJECT_ID = 'project_id'
NAMESPACE = 'namespace'
DEPLOYMENT_NAME = 'deployment_name'
SERVICE_ACCOUNT_FILE_NAME = 'service_account_file_name'
INCOMING_REQUEST_THRESHOLD_VALUE = 'threshold_value'
RESOURCE_REMOVAL_STRATEGY = 'resource_removal_strategy'
MIN_POD_REPLICAS = 'min_pod_replicas'
MAX_POD_REPLICAS = 'max_pod_replicas'
PROMETHEUS_SERVER_ADDRESS = 'prometheus_server_address'
PREDICTION_ERROR_MITIGATION_VALUE = 'prediction_error_mitigation_value'
ENABLE_CLOUD_METRIC_PUBLISHING = 'enable_cloud_metric_publishing'
ENABLE_CLOUD_LOGGING = 'enable_cloud_logging'

# paths
PATH_TO_SCALER_CONFIG_FILE = 'Dropins/scaler_config.yaml'
PATH_TO_SERVICE_ACCOUNT_CONFIG = 'Dropins/ServiceAccount/'
PATH_TO_DEEP_LEARNING_MODEL = 'Dropins/Model/model.pth.tar'

# datetime
DATE_TIME_FORMAT_STRING = '%Y-%m-%d %H:%M'

# monitoring metric
MONITORING_METRIC_TYPE = 'loadbalancing.googleapis.com/https/request_count'

# time series config
TIME_SERIES_TIME_COLUMN = "time"
TIME_SERIES_VALUE_COLUMN = "count"

# cloud logging
CLOUD_LOGGER_NAME = "my-test-log"

# metrics
PREDICTED_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE = 'custom.googleapis.com/global/predicted_request_count'
POD_REPLICA_COUNT_BY_DEPLOYMENT_METRIC_DESCRIPTOR_TYPE = 'custom.googleapis.com/global/pod_replica_count'
PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT_METRIC_DESCRIPTOR_TYPE = \
    'custom.googleapis.com/global/prometheus_server_metric_for_request_count'
PREDICTED_REQUEST_COUNT = "predicted request count"
POD_REPLICA_COUNT_BY_DEPLOYMENT = "pod replica count by deployment"
PROMETHEUS_SERVER_METRIC_FOR_REQUEST_COUNT = "prometheus server metric for request count"

# Prometheus
PROMQL_HAPROXY_REQUEST_COUNT = 'sum by (backend) (increase(haproxy_backend_http_responses_total[1m]))'
PROMQL_RESPONSE_METRIC = {'backend': 'allservers'}

# logging
LOG_MESSAGE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%d-%b-%y %H:%M:%S'
