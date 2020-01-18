FROM python:3.6

ENV IS_IN_DOCKER 1

# default every 5 minutes
ENV SYNC_INTERVAL_SECONDS 300

WORKDIR /app

COPY requirements.txt  requirements.txt 
RUN pip install -r requirements.txt 

COPY index.py index.py
COPY syncarr syncarr

CMD ["python", "/app/index.py"]