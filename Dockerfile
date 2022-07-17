FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY import.py .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y

RUN touch /var/log/cron.log
RUN echo '0 22 * * cd /app && python import.py > /logs/out.log 2>/logs/err.log \n' >> /etc/cron.d/water_usage_cron

RUN chmod 0644 /etc/cron.d/water_usage_cron
RUN crontab /etc/cron.d/water_usage_cron

RUN /etc/init.d/cron restart

CMD [ "cron", "-f"]
