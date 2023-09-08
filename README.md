# monitoring check for redis

## dependencies

 * `redis` Python(3) library, in debian/ubuntu `python3-redis`

## usage

```
./check_redis.py --help
usage: check_redis.py [-h] [-H HOST] [-p PORT] [-P PASSWORD] [-d DBNAME] [-t TIMEOUT] [-w WARNING] [-c CRITICAL] [-k KEY_VALUE]

monitoring plugin for redis-server

options:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Redis server to connect to. (default is 127.0.0.1)
  -p PORT, --port PORT  Redis port to connect to. (default is 6379)
  -P PASSWORD, --password PASSWORD
                        Redis password to connect to.
  -d DBNAME, --dbname DBNAME
                        Redis database name (default is db0)
  -t TIMEOUT, --timeout TIMEOUT
                        Number of seconds to wait before timing out and considering redis down
  -w WARNING, --warning WARNING
                        Warning threshold.
  -c CRITICAL, --critical CRITICAL
                        Critical threshold.
  -k KEY_VALUE, --key KEY_VALUE
                        Stat to monitor (memory_mb, hit_ratio, or custom)
```

## examples

```
./check_redis.py
OK REDIS version: 7.0.5, connected_clients: 1, db0: 1, used_memory_human: 672.77K, uptime_in_days: 2
```

```
./check_redis.py --key hit_ratio --critical 0 --warning 1
OK: Redis hit_ratio is 0 || hit_ratio=0;1;0;0;0
```

```
./check_redis.py --key memory_mb --critical 1 --warning 3
OK: Redis memory_mb is 8.98046875 || memory_mb=8.98046875;3;1;0;8.98046875
```
