from src.instance.instance import Instance
from typing import Union
from prometheus_client import start_http_server, Gauge, Counter
import logging
from random import randint
import time

logger = logging.getLogger(__name__)

METRICS_LABELS = ['instance_id', 'tenant_id', 'region']

class K8saasInstance(Instance):
    def __init__(
        self,
        id: str,
        tenant_id: str,
        region: str,
        metrics_port: int,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.region = region
        self.metrics_port = metrics_port
        self.label_tuple = (id, tenant_id, region)
        self.cluster_info = {}
        self.metrics = self._create_k8s_metrics()

    def _create_k8s_metrics(self) -> dict[str, Gauge | Counter]:
        k8s_metrics = dict()
        k8s_metrics["node_cpu_usage"] = Gauge(
            "k8s_node_cpu_usage", "CPU usage in percentage", METRICS_LABELS
        )
        # TODO: add metrics for each node separately
        k8s_metrics["node_memory_usage"] = Gauge(
            "k8s_node_memory_usage", "Memory usage in percentage", METRICS_LABELS
        )
        k8s_metrics["pod_count"] = Gauge(
            "k8s_pod_count", "Number of running pods", METRICS_LABELS
        )
        k8s_metrics["network_io"] = Gauge(
            "k8s_network_io", "Network I/O in bytes per second", METRICS_LABELS
        )
        # TODO: add a bunch of k8s metrics, such as pod, daemonset, deployment status, etc.
        return k8s_metrics

    def calculate_metrics(self) -> None:
        for metric in self.metrics:
            match metric:
                case "node_cpu_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(5, 100))
                case "node_memory_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(15, 100))
                case "pod_count":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(1, 50))
                case "network_io":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 100))
                case "disk_io":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 100))
                case _:
                    logger.warning(f"Unknown metric: {metric}")

    def start_metrics_server(self, scrape_interval_seconds: int = 60) -> None:
        start_http_server(self.metrics_port)
        logger.info(f"Metrics server started on port {self.metrics_port}")
        while True:
            self.calculate_metrics()
            time.sleep(scrape_interval_seconds)
