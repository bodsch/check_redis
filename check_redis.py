#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import sys
import argparse

EXIT_OK = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2
EXIT_UNKNONW = 3
EXIT_INVALID_AUTH = 3


class MonitoringPluginRedis(object):

    def __init__(self):
        """
        """
        cli_args = self.parse_args()

        self.host = cli_args.host
        self.port = cli_args.port
        self.password = cli_args.password
        self.dbname = cli_args.dbname
        self.timeout = cli_args.timeout
        self.key = cli_args.key_value
        self.warning = cli_args.warning
        self.critical = cli_args.critical

        try:
            self.conn = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                socket_timeout=self.timeout
            )
            self.info_out = self.conn.info()
            self.conn.ping()

        except Exception as e:
            print(f"CRITICAL REDIS : {e}")
            sys.exit(2)

    def parse_args(self):
        """
        """
        parser = argparse.ArgumentParser(
            description="monitoring plugin for redis-server, version: 1.0"
        )
        parser.add_argument(
            "-H", "--host",
            dest="host",
            help="Redis server to connect to. (default is 127.0.0.1)",
            default="127.0.0.1"
        )
        parser.add_argument(
            "-p", "--port",
            dest="port",
            help="Redis port to connect to. (default is 6379)",
            type=int,
            default=6379
        )
        parser.add_argument(
            "-P", "--password",
            dest="password",
            help="Redis password to connect to.",
            default=''
        )
        parser.add_argument(
            "-d", "--dbname",
            dest="dbname",
            help="Redis database name (default is db0)",
            default='db0'
        )
        parser.add_argument(
            "-t", "--timeout",
            dest="timeout",
            help="Number of seconds to wait before timing out and considering redis down",
            type=int,
            default=2
        )
        parser.add_argument(
            "-w", "--warning",
            dest="warning",
            type=int,
            help="Warning threshold."
        )
        parser.add_argument(
            "-c", "--critical",
            dest="critical",
            type=int,
            help="Critical threshold."
        )
        parser.add_argument(
            "-k", "--key",
            dest="key_value",
            help="Stat to monitor (memory_mb, hit_ratio, or custom)",
            default=None
        )

        return parser.parse_args()

    def get_version(self):

        return f"version: {self.info_out.get('redis_version')}"

    def get_client_connection(self):

        return f"connected_clients: {self.info_out.get('connected_clients')}"

    def get_number_keys(self):

        return f"{self.dbname}: {self.info_out.get(self.dbname).get('keys')}"

    def get_uptime(self):

        return f"uptime_in_days: {self.info_out.get('uptime_in_days')}"

    def get_used_memory(self):

        return f"used_memory_human: {self.info_out.get('used_memory_human')}"

    def check(self):
        """
        """
        number_keys = ''
        version = self.get_version()
        client_connected = self.get_client_connection()
        reverse_check = False
        exit_string = "OK"

        if self.dbname in str(self.info_out):
            number_keys = self.get_number_keys()

        memory = self.get_used_memory()
        uptime = self.get_uptime()

        # print(self.info_out)

        if self.key:
            if not self.warning or not self.critical:
                exit_string = "UNKNOWN"

                if not self.warning:
                    status = "UNKNOWN: Warning level required"
                if not self.critical:
                    status = "UNKNOWN: Critical level required"

                print(status)
                sys.exit(EXIT_UNKNONW)

            if self.key == "memory_mb":
                reverse_check = True
                info_value = int(
                    self.info_out.get("used_memory_rss") or self.info_out.get("used_memory")
                ) / (1024 * 1024)
            elif self.key == "hit_ratio":
                reverse_check = False
                hit = int(self.info_out.get("keyspace_hits"))
                miss = int(self.info_out.get("keyspace_misses"))

                if hit > 0 and miss > 0:
                    info_value = int(100 * hit) / (hit + miss)
                else:
                    info_value = 0
            else:
                info_value = int(self.info_out.get(self.key))

            if reverse_check:
                if int(info_value) < int(self.critical):
                    exit_string = "CRITICAL"
                elif int(info_value) < int(self.warning):
                    exit_string = "WARNING"
            else:
                if int(info_value) > int(self.critical):
                    exit_string = "CRITICAL"
                elif int(info_value) > int(self.warning):
                    exit_string = "WARNING"

            status = f"{exit_string}: Redis {self.key} is {info_value}"
            perfdata = f"{self.key}={info_value};{self.warning};{self.critical};0;{info_value}"

            print(f"{status}\n|{perfdata}")

        else:

            if number_keys == '':
                status = f"OK REDIS No keys, {version}, {memory}, {uptime}"
            else:
                status = f"OK REDIS {version}, {client_connected}, {number_keys}, {memory}, {uptime}"

            print(status)

        if exit_string == "OK":
            sys.exit(EXIT_OK)
        if exit_string == "WARNING":
            sys.exit(EXIT_WARNING)
        if exit_string == "UNKNOWN":
            sys.exit(EXIT_UNKNONW)
        else:
            sys.exit(EXIT_CRITICAL)


if __name__ == "__main__":
    """
    """
    server = MonitoringPluginRedis()
    server.check()
