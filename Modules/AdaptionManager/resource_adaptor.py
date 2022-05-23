import math
from kubernetes import client, config
from Modules.Constants import constants
from Modules.Logs import logger


def _get_deployment(api: client.AppsV1Api, configurations: dict) -> client.models.v1_deployment.V1Deployment:
    """
    Method to receive kubernetes deployment object model

    Parameters
    ----------
    api
        AppsV1Api object of gcloud
    configurations
        Configuration passed for the custom HPA programme
    """

    deployment = api.read_namespaced_deployment(
        namespace=configurations[constants.NAMESPACE],
        name=configurations[constants.DEPLOYMENT_NAME]
    )
    return deployment


def _scaling_command(
        api: client.AppsV1Api,
        deployment: client.models.v1_deployment.V1Deployment,
        number_of_pods: int,
        configurations: dict
) -> int:
    """
    Method to execute scaling commands to the Kubernetes Deployment

    Parameters
    ----------
    api
        AppsV1Api object of gcloud
    deployment
        Kubernetes deployment object
    number_of_pods
        Determined pod replicas count for the next minute
    configurations
        Configuration passed for the custom HPA programme

    Returns
    -------
    PrometheusConnect
        A PrometheusConnect object with connection details.
    """

    deployment.spec.replicas = number_of_pods
    request = api.patch_namespaced_deployment(
        name=deployment.metadata.name,
        namespace=deployment.metadata.namespace,
        body=deployment
    )
    updated_deployment = _get_deployment(api, configurations)
    ready_replicas = updated_deployment.status.ready_replicas
    return ready_replicas


def scaling_decisions(predicted_workload: int, configurations: dict):
    """
    Method to determine the pod count needed and communicate scaling decisions with the Kubernetes cluster

    Parameters
    ----------
    predicted_workload
        TimeSeries object with the predicted workload for the next minute.
    configurations
        Configuration passed for the custom HPA programme
    """

    config.load_kube_config()
    api = client.AppsV1Api()

    deployment = _get_deployment(api, configurations)
    current_pods_count = deployment.spec.replicas

    number_of_pods_for_next_interval = \
        int(math.ceil(predicted_workload / configurations[constants.INCOMING_REQUEST_THRESHOLD_VALUE]))

    if number_of_pods_for_next_interval > current_pods_count:

        pod_count_after_scaling = _scaling_command(api, deployment, number_of_pods_for_next_interval, configurations)

        if pod_count_after_scaling == number_of_pods_for_next_interval:
            logger.log_action(
                "info",
                "Pod count is increased from " + str(current_pods_count) + " to " + str(pod_count_after_scaling)
            )
            return pod_count_after_scaling

        logger.log_action(
            "info",
            "Pod count will be increased from " + str(current_pods_count) + " to " +
            str(number_of_pods_for_next_interval)
        )

        return pod_count_after_scaling

    elif number_of_pods_for_next_interval < current_pods_count:

        number_of_pods_for_next_interval = max(number_of_pods_for_next_interval,
                                               configurations[constants.MIN_POD_REPLICAS])

        surplus_pods = int(round((current_pods_count - number_of_pods_for_next_interval) * configurations[
            constants.RESOURCE_REMOVAL_STRATEGY]))

        if surplus_pods == 0:
            logger.log_action("info",
                              "Pod replica count of " + str(number_of_pods_for_next_interval) + " to be maintained")

            return number_of_pods_for_next_interval
        else:
            number_of_pods_for_next_interval = current_pods_count - surplus_pods
            pod_count_after_scaling = _scaling_command(api, deployment, number_of_pods_for_next_interval,
                                                       configurations)

            if pod_count_after_scaling == number_of_pods_for_next_interval:
                logger.log_action(
                    "info",
                    "Pod count is decreased from " + str(current_pods_count) + " to " + str(pod_count_after_scaling)
                )
                return pod_count_after_scaling

            logger.log_action(
                "info",
                "Pod count will be decreased from " + str(current_pods_count) + " to " + str(
                    number_of_pods_for_next_interval)
            )

            return pod_count_after_scaling

    else:

        logger.log_action("info", "Pod replica count of " + str(number_of_pods_for_next_interval) + " to be maintained")
        return number_of_pods_for_next_interval
