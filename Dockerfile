FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY import.py .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y

RUN touch /var/log/cron.log
RUN echo '15 22 * * * python /app/import.py >> /logs/import.log 2>&1 \n' >> /etc/cron.d/water_usage_cron

RUN chmod 0644 /etc/cron.d/water_usage_cron
RUN crontab /etc/cron.d/water_usage_cron
RUN touch /logs/import.log

RUN /etc/init.d/cron restart

CMD cron && tail -f /logs/import.log
