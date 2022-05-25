# Proactive Horizontal Pod Autoscaling System

This is a proactive custom Horizontal Pod Autoscaling (HPA) system for Kubernetes which forecasts the upcoming workload by analyzing the historical data of the target resource metrics using a deep learning technique called Temporal Convolutional Network (TCN), and proactively scale the number of pod replicas to handle the upcoming workload.

## Prerequisites

- [Python](https://www.python.org/downloads/) - Version 3.7+
- [Darts](https://unit8co.github.io/darts/quickstart/00-quickstart.html#Installing-Darts) - a Python library for easy manipulation and forecasting of time series.
- [Kubernetes Python Client](https://github.com/kubernetes-client/python) - Python client for the kubernetes API.
- [Prometheus API Client](https://github.com/AICoE/prometheus-api-client-python) - A Python wrapper for the Prometheus HTTP API.
- [Google Cloud Monitoring API](https://github.com/googleapis/python-monitoring) - Manages your Cloud Monitoring data and configurations
- [Google Cloud Logging](https://github.com/googleapis/python-logging) - Writes log entries and manages your Cloud Logging configuration
- [Pandas](https://pandas.pydata.org/getting_started.html) - Open source data analysis and manipulation tool
- [HAProxy Docker Image](https://hub.docker.com/_/haproxy) - The Reliable, High Performance TCP/HTTP Load Balancer
- [HAProxy Exporter Docker Image](https://hub.docker.com/r/prom/haproxy-exporter) - A simple server that periodically scrapes HAProxy stats and exports them via HTTP/JSON
- [Prometheus Docker Image](https://hub.docker.com/r/prom/prometheus/) - A systems and service monitoring system