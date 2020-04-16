#!/usr/bin/env python3

import CloudFlare
import CloudFlare.exceptions
import re

from common import tryit
from zonefile import RecordType as DnsRecordType, RecordData as DnsRecordData


class Record:
    def __init__(self, zone, record):
        self.zone = zone
        self.cf_record_id = record["id"]
        self.host = ".".join(record["name"].split(".")[:-2]) or "@"
        self.ttl = record["ttl"]
        self.raw_type = record["type"]
        self.type = tryit(DnsRecordType.parse)(self.raw_type) or None
        self.data = record["content"]

        if self.type == DnsRecordType.SRV:
            self.data = re.sub("\\s+", " ", self.data)
            self.data = f"{record['priority']} {self.data}"

        if self.type in [DnsRecordType.CNAME, DnsRecordType.SRV, DnsRecordType.MX]:
            recorddata = DnsRecordData.parse(self.data, self.type)
            self.data = recorddata.get_normalized_data()

    def __str__(self):
        if self.ttl == 1:
            return f"{self.host} IN {self.raw_type} {self.data}"
        else:
            return f"{self.host} {self.ttl} IN {self.raw_type} {self.data}"

    def update(self, record):
        new_data = record.data.get_normalized_data()
        cf = CloudFlare.CloudFlare()

        cf_record = {
            "name": self.host,
            "type": f"{self.type}",
            "content": new_data,
            "ttl": self.ttl
        }

        if self.type == DnsRecordType.SRV:
            name_parts = self.host.split(".")

            cf_service, cf_proto = name_parts[:2]
            cf_name = ".".join(name_parts[2:]) or "@"

            cf_record = {
                "type": "SRV",
                "data": {
                    "service": cf_service,
                    "proto": cf_proto,
                    "name": cf_name,
                    "priority": record.data.priority,
                    "weight": record.data.weight,
                    "port": record.data.port,
                    "target": record.data.target
                }
            }

        try:
            cf.zones.dns_records.put(self.zone.cf_zone_id, self.cf_record_id, data=cf_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            raise Exception('/zones.dns_records.put %s %s - %s' % (self.zone.domain, self.host, e))

        self.data = new_data

    def delete(self):
        cf = CloudFlare.CloudFlare()

        try:
            cf.zones.dns_records.delete(self.zone.cf_zone_id, self.cf_record_id)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            raise Exception('/zones.dns_records.delete %s %s - %s' % (self.zone.domain, self.host, e))

        self.zone.records.remove(self)

    def get_normalized_data(self):
        return self.data
