#!/usr/bin/env python3

import re

from ...common import DnsRecordType
from ...zonebase import Record as BaseRecord, TxtRecordData


class Record(BaseRecord):
    def __init__(self, record):
        super().__init__()

        self.id = record["id"]
        self.host = ".".join(record["name"].split(".")[:-2])
        self.type = record["type"]
        self.cf_proxied = record.get("proxied", False)

        self.set_data(record)

    def set_data(self, record):
        self.ttl = None if record["ttl"] == 1 else record["ttl"]

        content = record["content"]

        if self.type == DnsRecordType.SRV:
            content = re.sub("\\s+", " ", content)

        if self.type in [DnsRecordType.SRV, DnsRecordType.MX]:
            content = f"{record['priority']} {content}"

        if self.type in [DnsRecordType.TXT, DnsRecordType.SPF]:
            content = TxtRecordData.quote_data(content)

        self.data = content

    def compare_ttl(self, record: BaseRecord) -> bool:
        if self.cf_proxied:
            return True

        if hasattr(record, "cf_proxied") and record.cf_proxied:
            return True

        return super().compare_ttl(record)
