FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY import.py .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y

RUN touch /var/log/cron.log
RUN echo '0 0 * * cd /app && python import.py > /proc/1/fd/1 2>/proc/1/fd/2 \n' >> /etc/cron.d/water_usage_cron

RUN chmod 0644 /etc/cron.d/water_usage_cron
RUN crontab /etc/cron.d/water_usage_cron

RUN /etc/init.d/cron restart

RUN python import.py

CMD [ "cron", "-f"]
