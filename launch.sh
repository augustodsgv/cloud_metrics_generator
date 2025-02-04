echo "Building image..."
docker build . -t cloud_metrics_generator

PORT=8000

echo "Starting container..."
docker run --rm -p $PORT:$PORT \
    -e INSTANCE_ID="1" \
    -e TENANT_ID="1" \
    -e INSTANCE_REGION="a" \
    -e INSTANCE_TYPE="STRESS_TEST" \
    -e METRICS_PORT="$PORT" \
    -e SCRAPE_INTERVAL="1" \
    -e TIME_SERIES_COUNT="100_000" \
    -e LOG_LEVEL="INFO" \
    cloud_metrics_generator