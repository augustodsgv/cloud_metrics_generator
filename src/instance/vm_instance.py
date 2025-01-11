from src.instance.instance import Instance
from typing import Union
from prometheus_client import start_http_server, Gauge, Counter
import logging
from random import randint
import time

logger = logging.getLogger(__name__)

METRICS_LABELS = ['instance_id', 'tenant_id', 'region']

class VmInstance(Instance):
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
        self.metrics = self._create_vm_metrics()

    def _create_vm_metrics(self) -> dict[str, Gauge | Counter]:
        vm_metrics = dict()
        vm_metrics["cpu_usage"] = Gauge(
            "vm_cpu_usage", "CPU usage in percentage", METRICS_LABELS
        )
        vm_metrics["memory_usage"] = Gauge(
            "vm_memory_usage", "Memory usage in percentage", METRICS_LABELS
        )
        vm_metrics["storage_usage"] = Gauge(
            "vm_storage_usage", "Storage usage in percentage", METRICS_LABELS
        )
        vm_metrics["network_io"] = Gauge(
            "vm_network_io", "Network I/O in bytes per second", METRICS_LABELS
        )
        vm_metrics["disk_io"] = Gauge(
            "vm_disk_io", "Disk I/O in operations per second", METRICS_LABELS
        )
        return vm_metrics

    def calculate_metrics(self) -> None:
        for metric in self.metrics:
            match metric:
                case "cpu_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(5, 100))
                case "memory_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(15, 100))
                case "storage_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 100))
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
