FROM python:3

WORKDIR /cloud_metric_generator
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src src
EXPOSE 8000

CMD ["python3", "-m", "src.main"]