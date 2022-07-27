FROM python:3.11.0b5

ENV IS_IN_DOCKER 1

# default every 5 minutes
ENV SYNC_INTERVAL_SECONDS 300

WORKDIR /app

COPY requirements.txt  requirements.txt 
RUN pip install -r requirements.txt 

COPY . .

CMD ["python", "/app/index.py"]