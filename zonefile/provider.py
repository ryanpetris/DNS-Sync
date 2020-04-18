#!/usr/bin/env python3

import os

from .zone import Zone
from common import DnsRecordType
from queue import PriorityQueue
from typing import List, Union
from zonebase import ReadOnlyProvider as BaseReadOnlyProvider


class Provider(BaseReadOnlyProvider):
    @property
    def id(self) -> str:
        return "zonefile"

    def list_zones(self) -> List[str]:
        basepath = os.environ.get("ZONEFILE_PATH", ".")
        zones = []

        for file in os.listdir(basepath):
            filepath = os.path.join(basepath, file)

            if file.endswith(".db") and os.path.isfile(filepath):
                zones.append(".".join(file.split(".")[:-1]))

        return zones

    def get_zone(self, zone: str) -> Union[Zone, None]:
        basepath = os.environ.get("ZONEFILE_PATH", ".")
        filepath = os.path.join(basepath, f"{zone}.db")

        if not os.path.isfile(filepath):
            return None

        queue = PriorityQueue()
        zonedata = []
        priority = 0
        domain = ".".join(os.path.basename(filepath).split(".")[:-1])

        with open(filepath, "r") as f:
            for line in f.readlines():
                priority += 1
                queue.put((priority, line.strip()))

        while not queue.empty():
            priority, line = queue.get()

            if line.startswith("$INCLUDE"):
                _, include_file = line.split(" ")

                include_path = os.path.join(basepath, include_file)

                if not os.path.exists(include_path):
                    raise FileNotFoundError(f"Could not import file {include_path}")

                with open(include_path, "r") as f:
                    for line in reversed(f.readlines()):
                        priority -= 1
                        queue.put((priority, line.strip()))

                continue

            zonedata.append(line)

        return Zone("\n".join(zonedata), domain)

    def can_read_type(self, rtype: DnsRecordType) -> bool:
        return rtype in [
            DnsRecordType.A,
            DnsRecordType.AAAA,
            DnsRecordType.MX,
            DnsRecordType.SRV,
            DnsRecordType.CNAME,
            DnsRecordType.TXT,
            DnsRecordType.SPF,
            DnsRecordType.NS
        ]
