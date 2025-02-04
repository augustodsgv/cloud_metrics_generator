# Cloud Metrics Generator
This projects is meant to create an application that generates cloud-like metrics
for research porpouses, such as testing an observability stack

# Running the project
## Running with docker
The fastest way of starting the project is building the docker image locally
```sh
docker build . -t cloud_metrics_generator
```
If you need the container on other environment that supports docker, it might be
useful to send it to dockerhub. To do so, use the script
```
./push_to_dockerhub.sh
```
Finally run the container. It require the following environment variables
* `INSTANCE_TYPE`->Type of the instance. May be VM, DBAAS AND K8AAS for now
* `INSTANCE_ID`->ID of the instance. Might me a fake one
* `TENANT_ID`->ID of the tenant owner of the instance. Might me a fake one
* `INSTANCE_REGION`->Suposed region where the instance is running
It also supports some additional configurations
* `SCRAPE_INTERVAL`->Time in seconds that it takes to generate a new set of metrics. Should match the scrape interval of the prometheus.
* `TIME_SERIES_COUNT`->Indicates the amount of time series that stress test will generate. Used only by stress test 

Finally, run it:
```sh
docker run --rm -it  -e INSTANCE_ID=1234 -e TENANT_ID=5980980809 -e INSTANCE_REGION=gcp-sa-east -e INSTANCE_TYPE=dbaas -p 8000:8000 cloud_metric_generator   
``` 
The metrics should appear on `localhost:8000`

## Using local python
If you want to run locally, first create an virtual environment
```sh
python3 -m venv venv
source venv/bin/activate
```
Then get the libraries
```sh
pip install -r requirements.txt
```
Set the environment variables
```
export INSTANCE_ID=1234
export TENANT_ID=5980980809
export INSTANCE_REGION=gcp-sa-east
export INSTANCE_TYPE=dbaas 
```
And finally run it
```sh
python3 -m src.main
```

# Authors
augustodsgv