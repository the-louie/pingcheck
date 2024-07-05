import re
import subprocess
from influxdb import InfluxDBClient

response = subprocess.Popen('/usr/bin/speedtest --accept-license --accept-gdpr', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

ping = re.search('Latency:\s+(.*?)\s', response, re.MULTILINE)
ping_low = re.search('Latency:.*?low:\s+(.*?)ms', response, re.MULTILINE)
ping_high = re.search('Latency:.*?high:\s+(.*?)ms', response, re.MULTILINE)
download = re.search('Download:\s+(.*?)\s', response, re.MULTILINE)
upload = re.search('Upload:\s+(.*?)\s', response, re.MULTILINE)
jitter = re.search('Latency:.*?jitter:\s+(.*?)ms', response, re.MULTILINE)
packetloss = re.search('Packet Loss:\s+(.*?)%', response, re.MULTILINE)

ping = ping.group(1)
ping_low = ping_low.group(1)
ping_high = ping_high.group(1)
download = download.group(1)
upload = upload.group(1)
jitter = jitter.group(1)
packetloss = packetloss.group(1)

speed_data = [
    {
        "measurement" : "internet_speed",
        "tags" : {
            "host": "louie"
        },
        "fields" : {
            "download": float(download),
            "upload": float(upload),
            "ping": float(ping),
            "jitter": float(jitter),
            "ping_low": float(ping_low),
            "ping_high": float(ping_high),
            "packetloss": float(packetloss)
        }
    }
]
client = InfluxDBClient('localhost', 8086, 'user', 'password', 'dbname')

client.write_points(speed_data)
