#!/usr/bin/env python3

from __future__ import annotations

from ...common import DnsRecordType
from ...zonebase import Record as BaseRecord


class Record(BaseRecord):
    def __init__(self, data):
        super().__init__()

        self.host = data["host"] if "host" in data else "@"
        self.type = data["type"]
        self.id = None

        self.set_data(data)

    def set_data(self, data):
        self.id = data["id"]
        self.ttl = data["ttl"] or None

        if self.type in [DnsRecordType.SRV, DnsRecordType.MX]:
            self.data.raw = f"{data['priority'] if 'priority' in data else 0} {data['answer']}"
        elif self.type in [DnsRecordType.TXT, DnsRecordType.SPF]:
            self.data.normalized = data["answer"]
        else:
            self.data.raw = data["answer"]
