# Proactive Horizontal Pod Autoscaling System

This is a proactive custom Horizontal Pod Autoscaling (HPA) system for Kubernetes which forecasts the upcoming workload by analyzing the historical data of the target resource metrics using a deep learning technique called Temporal Convolutional Network (TCN), and proactively scale the number of pod replicas to handle the upcoming workload.