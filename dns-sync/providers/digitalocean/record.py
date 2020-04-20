#!/usr/bin/env python3

from __future__ import annotations

from ...common import DnsRecordType
from ...zonebase import Record as BaseRecord


class Record(BaseRecord):
    def __init__(self, data):
        super().__init__()

        self.host = data["name"]
        self.type = data["type"]
        self.id = None

        self.set_data(data)

    def set_data(self, data):
        self.id = data["id"]
        self.ttl = data["ttl"] or None

        if self.type in [DnsRecordType.TXT, DnsRecordType.SPF]:
            self.data.normalized = data["data"]
        elif self.type in [DnsRecordType.A, DnsRecordType.AAAA]:
            self.data.raw = data["data"]

        self.data.priority = data["priority"]
        self.data.weight = data["weight"]
        self.data.port = data["port"]
        self.data.target = data["data"]
