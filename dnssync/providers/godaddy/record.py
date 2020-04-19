#!/usr/bin/env python3

from __future__ import annotations

from ...common import DnsRecordType
from ...zonebase import Record as BaseRecord
from typing import Union


class Record(BaseRecord):
    def __init__(self, data):
        super().__init__()

        if isinstance(data, BaseRecord):
            self.host = data.host
            self.type = data.type

            self.set_data(data)
            return

        self.host = data["name"]
        self.type = data["type"]
        self.ttl = data["ttl"] or None

        if self.type == DnsRecordType.SRV:
            if self.host == "@":
                self.host = f"{data['service']}.{data['protocol']}"
            else:
                self.host = f"{data['service']}.{data['protocol']}.{data['name']}"

        if self.type in [DnsRecordType.TXT, DnsRecordType.SPF]:
            self.data.normalized = data["data"]
        elif self.type not in [DnsRecordType.MX, DnsRecordType.CNAME, DnsRecordType.SRV]:
            self.data.raw = data["data"]
        else:
            self.data.target = data["data"]

        if "priority" in data:
            self.data.priority = data["priority"]

        if "weight" in data:
            self.data.weight = data["weight"]

        if "port" in data:
            self.data.port = data["port"]

    def set_data(self, data: BaseRecord):
        self.ttl = data.ttl
        self.data = data.data
