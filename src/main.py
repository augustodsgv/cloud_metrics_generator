from src.instance import VmInstance, DbaasInstance, K8saasInstance, InstanceTypeDoesNotExist

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


def main():
    missing_vars = [var for var in ['INSTANCE_ID', 'TENANT_ID', 'INSTANCE_REGION', 'INSTANCE_TYPE'] if var not in os.environ]
    if missing_vars:
        raise ValueError(f'Missing environment variables: {", ".join(missing_vars)}')
    
    instance_id = os.environ['INSTANCE_ID']
    tenant_id = os.environ['TENANT_ID']
    instance_region = os.environ['INSTANCE_REGION']
    instance_type = os.environ['INSTANCE_TYPE']
    scrape_interval = int(os.environ.get('SCRAPE_INTERVAL', '60'))
    metric_port = int(os.environ.get('METRIC_PORT', '8000'))
    has_defect = os.environ.get('HAS_DEFECT', 'False').lower() == 'true'
    # TODO: implement a way of setting a specific defect for each instance

    metric_generator = ...
    match instance_type.upper():
        case 'VM':
            metric_generator = VmInstance(
                id=instance_id,
                tenant_id=tenant_id,
                region=instance_region,
                has_random_defects=has_defect,
                metrics_port=metric_port
            )
        case 'DBAAS':
            metric_generator = DbaasInstance(
                id=instance_id,
                tenant_id=tenant_id,
                region=instance_region,
                has_random_defects=has_defect,
                metrics_port=metric_port
            )
        case 'K8SAAS':
            metric_generator = K8saasInstance(    id=instance_id,
                tenant_id=tenant_id,
                region=instance_region,
                has_random_defects=has_defect,
                metrics_port=metric_port
            )
        case _ :
            raise InstanceTypeDoesNotExist(f'Instance type {instance_type} does not exists')
        
    logger.info(f'Instance set to {instance_type}')
    logger.info(f'Scrape intervale set to {scrape_interval} seconds')
    logger.info(f'Metrics server will run on port {metric_port}')
    logger.info(f'Instance id: {instance_id}')
    logger.info(f'Tenant id: {tenant_id}')
    logger.info(f'Region: {instance_region}')
    logger.info(f'Has defects: {metric_generator.defects}')
    metric_generator.start_metrics_server(scrape_interval_seconds=scrape_interval)

if __name__ == '__main__':
    main()