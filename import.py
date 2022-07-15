import requests
from datetime import datetime
import csv
from io import StringIO
import yaml
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

# load config
with open("/data/config.yml", "r") as stream:
    try:
        config_yaml = yaml.safe_load(stream)
        db_config = config_yaml['db_config']
        veolia_config = config_yaml['veolia_config']
    except yaml.YAMLError as exc:
        print(exc)

# InfluxDB data
token = db_config['influx_db_token']
org = db_config['influx_db_org']
bucket = db_config['influx_db_bucket']
url = db_config['influx_db_url']
client = InfluxDBClient(url=url, token=token)

# Veolia config
veolila_login_payload = {
	"name": veolia_config['name'],
	"pass": veolia_config['pass'],
	"remember_me": veolia_config['remember_me'],
    "form_build_id": veolia_config['form_build_id'],
    "form_id": "user_login"
}

def success_cb(details, data):
    url, token, org = details
    print(url, token, org)
    data = data.decode('utf-8').split('\n')
    print('Total Rows Inserted:', len(data))

def error_cb(details, data, exception):
    print(exception)

def retry_cb(details, data, exception):
    print('Retrying because of an exception:', exception)

write_api = client.write_api(   success_callback=success_cb,
                                error_callback=error_cb,
                                retry_callback=retry_cb,
                                write_options=SYNCHRONOUS)


session_requests = requests.session()
login_url = "https://mywater.veolia.us/user/login?current=node/28314916"

result = session_requests.post(
	login_url,
	data = veolila_login_payload,
	headers = dict(referer=login_url)
)

print("Login: " + str(result.status_code))

end_date = datetime.today() - timedelta(days=1) # yesterday
start_date = end_date - timedelta(days=30) # 30 days before yesterday

end_date_str = end_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

usage_download_url = f"https://mywater.veolia.us/usage_download/desktop/{start_date_str}-{end_date_str}?destination=water-usage"
result = session_requests.get(
	usage_download_url,
	headers = dict(referer = usage_download_url)
)


print("Usage Download: " + str(result.status_code))

csv_data = StringIO(result.content.decode())

consumption_data =  csv.reader(csv_data)
# skip header line
next(consumption_data)

records = []

for row in consumption_data:
    meter = row[0]
    date_time = row[2]
    try:
        consumption = float(row[3])
    except ValueError:
        continue
    consumption_l = 3.785 * consumption
    ts = datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S').isoformat()
    record = [
        {
            "measurement": "water_consumption",
            "tags": {
                "meter": meter,
                "provider": "Veolia"
            },
            "time": ts,
            "fields": {
                "consumption_gal": consumption,
                "consumption_liter": consumption_l
            }
        }
    ]
    records.append(record)

print(len(records))
write_api.write(bucket, org, records)
