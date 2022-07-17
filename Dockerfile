FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY import.py .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install cron -y

RUN echo '49 22 * * * /usr/local/bin/python /app/import.py > /proc/1/fd/1 2>/proc/1/fd/2 \n' >> /etc/cron.d/water_usage_cron

RUN chmod 0744 /etc/cron.d/water_usage_cron
RUN crontab /etc/cron.d/water_usage_cron
RUN date

RUN /etc/init.d/cron restart

CMD ["cron", "-f"]

