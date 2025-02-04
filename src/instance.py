from abc import ABC, abstractmethod
from prometheus_client import start_http_server, Gauge, Counter
import random
import logging
import time

logger = logging.getLogger(__name__)

class InstanceTypeDoesNotExist(Exception):
    ...

class DefectTypeDoesNotExist(Exception):
    ...

class Instance(ABC):
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
        """
        The has_defect attribute is used to simulate a defect in the instance.
        When enabled, will produce abdorminal metrics values.
        Each instance has its own possible defects.
        """
        self.gauge_metrics = dict()
        self.counter_metrics = dict()
        self.label_tuple = ...
        self.metric_values = ...
        self.defects = ...
        # self.label_tuple = (id, tenant_id, region)
        # self.metrics = self._create_metrics()
        # self.metric_values = self._set_metrics_possible_values(defects)

    def calculate_metrics(self) -> None:
        for metric_name, metric in self.gauge_metrics.items():
            min_value, max_value = self.metric_values[metric_name]
            metric_measurement = random.randint(min_value, max_value)
            metric.labels(*self.label_tuple).set(metric_measurement)

        for metric_name, metric in self.counter_metrics.items():
            min_value, max_value = self.metric_values[metric_name]
            metric_measurement = random.randint(min_value, max_value)
            metric.labels(*self.label_tuple).inc(metric_measurement)

    def start_metrics_server(self, scrape_interval_seconds: int = 60) -> None:
        start_http_server(self.metrics_port)
        logger.info(f"Metrics server started on port {self.metrics_port}")
        while True:
            self.calculate_metrics()
            time.sleep(scrape_interval_seconds)

    @abstractmethod
    def _set_metrics_possible_values(self) -> dict[str, tuple[int]]:
        """
        Sets the range of possible values for each metric.
        By default, a metric can have a value between 0 and 80.
        If a there is a defect, the range will be between 90 and 100.
        """
        ...

    @abstractmethod
    def _create_metrics(self) -> None:
        """
        Creates all instances metrics.
        Metrics are grouped by their type. For now, we only have Gauge an counter metrics
        """
        # Counter
        """
        Creates the metrics of the instance.
        This has to be manually created because of the different behavior of each metric.
        """
        ...

class VmInstance(Instance):
    VM_DEFECTS = ["cpu_usage", "memory_usage", "storage_usage", "network_io", "disk_io"]
    VM_LABELS = ["instance_id", "tenant_id", "region"]
    def __init__(
        self,
        id: str,
        tenant_id: str,
        region: str,
        metrics_port: int,
        has_random_defects: bool = False,
        defects: list[str] = [],
    ):
        super().__init__(id, tenant_id, region, metrics_port)
        self.label_tuple = (id, tenant_id, region)
        self._create_metrics()
        if has_random_defects:
            """
            Creates a random set of defects for the VM instance.
            """
            defects_count = random.randint(1, len(self.VM_DEFECTS))
            defects = random.sample(self.VM_DEFECTS, defects_count)
        self.defects = defects
        self.metric_values = self._set_metrics_possible_values()

    def _set_metrics_possible_values(self) -> dict[str, tuple[int]]:
        """
        Sets the range of possible values for each metric.
        By default, a metric can have a value between 0 and 80.
        If a there is a defect, the range will be between 90 and 100.
        """

        metrics_possible_values = {
            "cpu_usage": (0, 80),
            "memory_usage": (0, 80),
            "storage_usage": (0, 80),
            "network_io": (0, 80),
            "disk_io": (0, 80),
        }

        for defect in self.defects:
            metrics_possible_values[defect] = (90, 100)
        return metrics_possible_values

    def _create_metrics(self) -> None:
        """
        Creates all instances metrics.
        Metrics are grouped by their type. For now, we only have Gauge an counter metrics
        """
        # Counter
        """
        Creates the metrics of the VM instance.
        This has to be manually created because of the different behavior of each metric.
        """
        
        self.gauge_metrics["cpu_usage"] = Gauge(
            "vm_cpu_usage", "CPU usage in percentage", self.VM_LABELS
        )
        self.gauge_metrics["memory_usage"] = Gauge(
            "vm_memory_usage", "Memory usage in percentage", self.VM_LABELS
        )
        self.gauge_metrics["storage_usage"] = Gauge(
            "vm_storage_usage", "Storage usage in percentage", self.VM_LABELS
        )
        self.gauge_metrics["network_io"] = Gauge(
            "vm_network_io", "Network I/O in bytes per second", self.VM_LABELS
        )
        self.gauge_metrics["disk_io"] = Gauge(
            "vm_disk_io", "Disk I/O in operations per second", self.VM_LABELS
        )
    
class DbaasInstance(Instance):
    DBAAS_DEFECTS = ["cpu_usage", "memory_usage", "storage_usage", "network_usage", "db_connections", "db_queries", "query_latency", "errors", "up"]
    DBAAS_LABELS = ["instance_id", "tenant_id", "region"]

    def __init__(
        self,
        id: str,
        tenant_id: str,
        region: str,
        metrics_port: int,
        has_random_defects: bool = False,
        defects: list[str] = [],
    ):
        super().__init__(id, tenant_id, region, metrics_port)
        self.label_tuple = (id, tenant_id, region)
        self._create_metrics()

        if has_random_defects:
            """
            Creates a random set of defects for the DBAAS instance.
            """
            defects_count = random.randint(1, len(self.DBAAS_DEFECTS))
            defects = random.sample(self.DBAAS_DEFECTS, defects_count)
        self.defects = defects
        self.metric_values = self._set_metrics_possible_values()

    def _set_metrics_possible_values(self) -> dict[str, tuple[int]]:
        """
        Sets the range of possible values for each metric.
        By default, a metric can have a value between 0 and 80.
        If a there is a defect, the range will be between 90 and 100.
        """
        # TODO: make counter metrics a different possible values
        metrics_possible_values = {
            "cpu_usage": (0, 80),
            "memory_usage": (0, 80),
            "storage_usage": (20, 80),
            "network_usage": (0, 80),
            "db_connections": (10, 80),
            "db_queries": (0, 80),
            "query_latency": (5, 50),
            "errors": (0, 0),
            "up": (1, 1),
        }
        # Define here how a defect metric value should look like
        for defect in self.defects:
            match defect:
                case "up":
                    metrics_possible_values[defect] = (0, 1)
                case 'errors':
                    metrics_possible_values[defect] = (1, 5)
                case "db_connections":
                    metrics_possible_values[defect] = (500, 500)
                case "db_queries":
                    metrics_possible_values[defect] = (0, 0)
                case "query_latency":
                    metrics_possible_values[defect] = (60, 6000)
                case _:
                    metrics_possible_values[defect] = (90, 100)

        return metrics_possible_values

    def _create_metrics(self) -> None:
        """
        Creates all instances metrics.
        Metrics are grouped by their type. For now, we only have Gauge an counter metrics
        """
        # Counter
        self.gauge_metrics["cpu_usage"] = Gauge(
            "dbaas_cpu_usage", "CPU usage in percentage", self.DBAAS_LABELS
        )
        self.gauge_metrics["memory_usage"] = Gauge(
            "dbaas_memory_usage", "Memory usage in percentage", self.DBAAS_LABELS
        )
        self.gauge_metrics["storage_usage"] = Gauge(
            "dbaas_storage_usage", "Storage usage in percentage", self.DBAAS_LABELS
        )
        self.gauge_metrics["network_usage"] = Gauge(
            "dbaas_network_usage", "Network usage in percentage", self.DBAAS_LABELS
        )
        self.gauge_metrics["db_connections"] = Gauge(
            "dbaas_db_connections", "Number of database connections", self.DBAAS_LABELS
        )
        self.gauge_metrics["query_latency"] = Gauge(
            "dbaas_query_latency", "Latency of database queries in milliseconds", self.DBAAS_LABELS
        )
        self.gauge_metrics["errors"] = Gauge(
            "dbaas_errors", "Number of errors", self.DBAAS_LABELS
        )
        self.gauge_metrics["up"] = Gauge(
            "up", "DBaaS instance status", self.DBAAS_LABELS
        )
        # TODO: add availability, node leadership, etc.

        # Gauge
        self.counter_metrics["db_queries"] = Counter(
            "dbaas_db_queries", "Number of database queries", self.DBAAS_LABELS
        )
    
class K8saasInstance(Instance):
    K8SAAS_DEFECTS = ["cpu_usage", "memory_usage", "storage_usage", "network_usage", "pods", "services", "nodes", "up"]
    K8SAAS_LABELS = ["instance_id", "tenant_id", "region"]

    def __init__(
        self,
        id: str,
        tenant_id: str,
        region: str,
        metrics_port: int,
        has_random_defects: bool = False,
        defects: list[str] = [],
    ):
        super().__init__(id, tenant_id, region, metrics_port)
        self.label_tuple = (id, tenant_id, region)
        self._create_metrics()

        if has_random_defects:
            """
            Creates a random set of defects for the DBAAS instance.
            """
            defects_count = random.randint(1, len(self.K8SAAS_DEFECTS))
            defects = random.sample(self.K8SAAS_DEFECTS, defects_count)

        self.defects = defects
        self.metric_values = self._set_metrics_possible_values()

    def _set_metrics_possible_values(self) -> dict[str, tuple[int]]:
        """
        Sets the range of possible values for each metric.
        By default, a metric can have a value between 0 and 80.
        If a there is a defect, the range will be between 90 and 100.
        """
        metrics_possible_values = {
            "cpu_usage": (0, 80),
            "memory_usage": (0, 80),
            "storage_usage": (0, 80),
            "network_usage": (0, 80),
            "pods": (200, 200),
            "pods_down": (0, 0),
            "services": (40, 40),
            "services_down": (40, 40),
            "nodes": (5, 5),
            "nodes_down": (0, 0),
            "up": (1, 1),
        }

        for defect in self.defects:
            match defect:
                case "up":
                    metrics_possible_values[defect] = (0, 1)
                case "services":
                    metrics_possible_values[defect] = (10, 40)
                case "pods":
                    metrics_possible_values[defect] = (50, 200)
                case "nodes":
                    metrics_possible_values[defect] = (2, 5)
                case _:
                    metrics_possible_values[defect] = (0, 80)

        return metrics_possible_values

    def _create_metrics(self) -> None:
        """
        Creates all instances metrics.
        Metrics are grouped by their type. For now, we only have Gauge an counter metrics
        """
        # Counter
        """
        Creates the metrics of the K8saaS instance.
        This has to be manually created because of the different behavior of each metric.
        """
        self.gauge_metrics["cpu_usage"] = Gauge(
            "k8saas_cpu_usage", "CPU usage in percentage", self.K8SAAS_LABELS
        )
        self.gauge_metrics["memory_usage"] = Gauge(
            "k8saas_memory_usage", "Memory usage in percentage", self.K8SAAS_LABELS
        )
        self.gauge_metrics["storage_usage"] = Gauge(
            "k8saas_storage_usage", "Storage usage in percentage", self.K8SAAS_LABELS
        )
        self.gauge_metrics["network_usage"] = Gauge(
            "k8saas_network_usage", "Network usage in percentage", self.K8SAAS_LABELS
        )
        self.gauge_metrics["pods"] = Gauge(
            "k8saas_pods", "Number of pods", self.K8SAAS_LABELS
        )
        self.gauge_metrics["pods_down"] = Gauge(
            "k8saas_pods_down", "Number of pods not in ready state", self.K8SAAS_LABELS
        )
        self.gauge_metrics["services"] = Gauge(
            "k8saas_services", "Number of services in the cluster", self.K8SAAS_LABELS
        )
        self.gauge_metrics["services_down"] = Gauge(
            "k8saas_services_down", "Number of services down", self.K8SAAS_LABELS
        )
        self.gauge_metrics["nodes"] = Gauge(
            "k8saas_nodes", "Number of nodes in the cluster", self.K8SAAS_LABELS
        )
        self.gauge_metrics["nodes_down"] = Gauge(
            "k8saas_nodes_down", "Number of nodes down in the cluster", self.K8SAAS_LABELS
        )
        self.gauge_metrics["up"] = Gauge(
            "up", "K8saaS instance status", self.K8SAAS_LABELS
        )

class StressTestInstance(Instance):
    """
    Creates a stress test instance that will generate tons of time series.
    This is achieved by creating a lot of distinc gauge metrics, creating many time series.
    For now, creates only a gauges. 
    """
    STRESS_TEST_LABELS = ["instance_id", "tenant_id", "region"]
    STRESS_TEST_DEFECTS = []

    def __init__(
        self,
        id: str,
        tenant_id: str,
        region: str,
        metrics_port: int,
        has_random_defects: bool = False,
        defects: list[str] = [],
        time_series_count: int = 100,
    ):
        super().__init__(id, tenant_id, region, metrics_port)
        self.label_tuple = (id, tenant_id, region)

        """
        Generating time_series_count labels for the stress test instance
        """
        self.time_series_count = time_series_count
        self._create_metrics()


        self.defects = defects
        self.metric_values = self._set_metrics_possible_values()

    def _create_metrics(self) -> None:
        """
        Creates a stress_test gauge metric with time_series_count labels
        """
        for i in range(self.time_series_count):
            metric_name = f"stress_test_gauge_{i}"
            self.gauge_metrics[metric_name] = Gauge(
                metric_name, f"A Gauge of other many. Index: {i}",  self.STRESS_TEST_LABELS
            )

    def _set_metrics_possible_values(self) -> dict[str, tuple[int]]:
        """
        Sets the range of possible values for the metrics.
        """
        metrics_possible_values = dict()
        for i in range(self.time_series_count):
            metric_name = f"stress_test_gauge_{i}"
            metrics_possible_values[metric_name] = (0, 100)

        return metrics_possible_values