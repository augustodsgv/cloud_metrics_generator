from src.instance.instance import Instance
from typing import Union
from prometheus_client import start_http_server, Gauge, Counter
import logging
from random import randint
import time

logger = logging.getLogger(__name__)

METRICS_LABELS = ['instance_id', 'tenant_id', 'region']

class DbaasInstance(Instance):
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
        self.metrics = self._create_dbaas_metrics()

    def _create_dbaas_metrics(self) -> dict[str, Gauge | Counter]:
        dbaas_metrics = dict()
        dbaas_metrics["cpu_usage"] = Gauge(
            "dbaas_cpu_usage", "CPU usage in percentage", METRICS_LABELS
        )
        dbaas_metrics["memory_usage"] = Gauge(
            "dbaas_memory_usage", "Memory usage in percentage", METRICS_LABELS
        )
        dbaas_metrics["storage_usage"] = Gauge(
            "dbaas_storage_usage", "Storage usage in percentage", METRICS_LABELS
        )
        dbaas_metrics["network_usage"] = Gauge(
            "dbaas_network_usage", "Network usage in percentage", METRICS_LABELS
        )
        dbaas_metrics["db_connections"] = Gauge(
            "dbaas_db_connections", "Number of database connections", METRICS_LABELS
        )
        dbaas_metrics["db_queries"] = Counter(
            "dbaas_db_queries", "Number of database queries", METRICS_LABELS
        )
        dbaas_metrics["query_latency"] = Gauge(
            "dbaas_query_latency", "Latency of database queries in milliseconds", METRICS_LABELS
        )
        dbaas_metrics["errors"] = Gauge(
            "dbaas_errors", "Number of errors", METRICS_LABELS
            )
        dbaas_metrics["up"] = Gauge(
            "up", "DBaaS instance status", METRICS_LABELS
            )
        # TODO: add availability, node leadership, etc.
        return dbaas_metrics

    def calculate_metrics(self) -> None:
        for metric in self.metrics:
            match metric:
                case "cpu_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(5, 100), )
                case "memory_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(15, 100))
                case "storage_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 100))
                case "network_usage":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 100))
                case "db_connections":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(10, 150))
                case "db_queries":
                    self.metrics[metric].labels(*self.label_tuple).inc(randint(0, 10))
                case "query_latency":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(100, 1000))
                case "errors":
                    self.metrics[metric].labels(*self.label_tuple).set(randint(0, 5))
                case "up":
                    if randint(0, 100) < 5:  # 5% chance of being down
                        self.metrics[metric].labels(*self.label_tuple).set(0)
                    else:
                        self.metrics[metric].labels(*self.label_tuple).set(1)
                case _:
                    logger.warning(f"Unknown metric: {metric}")

    def start_metrics_server(self, scrape_interval_seconds: int = 60) -> None:
        start_http_server(self.metrics_port)
        logger.info(f"Metrics server started on port {self.metrics_port}")
        while True:
            self.calculate_metrics()
            time.sleep(scrape_interval_seconds)
