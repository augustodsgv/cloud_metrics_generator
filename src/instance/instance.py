from abc import ABC, abstractmethod

class Instance(ABC):
    @abstractmethod
    def calculate_metrics(self) -> None:
        pass

    @abstractmethod
    def start_metrics_server(self, scrape_interval_seconds: int = 60) -> None:
        pass