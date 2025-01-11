from src.instance.dbaas_instance import DbaasInstance
from src.instance.vm_instance import VmInstance
from src.instance.k8saas_instance import K8saasInstance

import prometheus_client
import os
import logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'ERROR').upper()
)

logger = logging.getLogger(__name__)

# Removing default python metrics
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)

class InstanceTypeDoesNotExist(Exception):
    ...

def main():
    instance_type = os.environ.get('INSTANCE_TYPE', 'default').upper()
    scrape_interval = int(os.environ.get('SCRAPE_INTERVAL', '60'))
    metric_port = int(os.environ.get('METRIC_PORT', '8000'))

    instance_id = os.environ['INSTANCE_ID']
    tenant_id = os.environ['TENANT_ID']
    instance_region = os.environ['INSTANCE_REGION']
    metric = ...
    match instance_type:
        case 'DEFAULT':
            raise NotImplementedError('Default instance type not implemented')
        case 'VM':
            metric = VmInstance(instance_id, tenant_id, instance_region, metrics_port=metric_port)
        case 'DBAAS':
            metric = DbaasInstance(instance_id, tenant_id, instance_region, metrics_port=metric_port)
        case 'K8SAAS':
            metric = K8saasInstance(instance_id, tenant_id, instance_region, metrics_port=metric_port)
        case _ :
            raise InstanceTypeDoesNotExist(f'Instance type {instance_type} does not exists')
    logger.info(f'Instance set to {instance_type}')
    logger.info(f'Scrape intervale set to {scrape_interval} seconds')
    metric.start_metrics_server(scrape_interval_seconds=scrape_interval)

if __name__ == '__main__':
    main()