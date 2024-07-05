import re
import datetime
import subprocess
import time
from influxdb import InfluxDBClient

TARGETS=["dynamodb.eu-north-1.amazonaws.com", "link-c2-wn-2.junet.se", "netnod-ix-cph-green-9000.amazon.com"]

def main(target):
    response = subprocess.Popen(f'ping -nUc 3 -i 0.5 {target}', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

    """
    --- dynamodb.eu-north-1.amazonaws.com ping statistics ---
    3 packets transmitted, 3 received, 0% packet loss, time 1003ms
    rtt min/avg/max/mdev = 18.592/18.686/18.785/0.078 ms
    """

    ping_min = re.search('rtt min/avg/max/mdev = ([\d\.]+)/[\d\.]+/[\d\.]+/[\d\.]+ ms', response, re.MULTILINE)
    ping_avg = re.search('rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms', response, re.MULTILINE)
    ping_max = re.search('rtt min/avg/max/mdev = [\d\.]+/[\d\.]+/([\d\.]+)/[\d\.]+ ms', response, re.MULTILINE)
    ping_mdev = re.search('rtt min/avg/max/mdev = [\d\.]+/[\d\.]+/[\d\.]+/([\d\.]+) ms', response, re.MULTILINE)
    ping_pl = re.search('([\d\.]+)% packet loss', response, re.MULTILINE)

    ping_min = ping_min.group(1)
    ping_avg = ping_avg.group(1)
    ping_max = ping_max.group(1)
    ping_mdev = ping_mdev.group(1)
    ping_pl = ping_pl.group(1)

    speed_data = [
        {
            "measurement" : "internet_latency",
            "tags" : {
                "host": "louie",
                "target": target
            },
            "fields" : {
                "ping_min": float(ping_min),
                "ping_avg": float(ping_avg),
                "ping_max": float(ping_max),
                "ping_mdev": float(ping_mdev),
                "ping_pl": float(ping_pl),
            }
        }
    ]
    client = InfluxDBClient('localhost', 8086, 'user', 'pass', 'dbname')

    client.write_points(speed_data)


if __name__ == '__main__':
    while True:
        start = datetime.datetime.now()
        for host in TARGETS:
            main(host)

        delta = (datetime.datetime.now() - start).microseconds
        print(5 - (delta / 100000))
        time.sleep(5 - (delta / 100000))
