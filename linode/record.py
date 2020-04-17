#!/usr/bin/env python3

from .api import StaticApi
from common import tryit
from zonefile import RecordType as DnsRecordType


class Record:
    valid_record_types = [
        DnsRecordType.A,
        DnsRecordType.AAAA,
        DnsRecordType.MX,
        DnsRecordType.CNAME,
        DnsRecordType.TXT,
        DnsRecordType.SRV,
        DnsRecordType.PTR
    ]

    target_is_hostname_types = [
        DnsRecordType.MX,
        DnsRecordType.CNAME,
        DnsRecordType.SRV
    ]

    def __init__(self, data, zone):
        self.zone = zone

        self.__set_data(data)

    def __set_data(self, data):
        self.id = data["id"]
        self.host = data["name"] or "@"
        self.target = data["target"]
        self.priority = data["priority"]
        self.weight = data["weight"]
        self.port = data["port"]
        self.service = data["service"]
        self.protocol = data["protocol"]
        self.ttl = data["ttl_sec"]
        self.raw_type = data["type"]
        self.type = tryit(DnsRecordType.parse)(self.raw_type) or None

    def get_normalized_target(self):
        cls = self.__class__

        if self.type in cls.target_is_hostname_types:
            if not self.target.endswith("."):
                return f"{self.target}."

        return self.target

    def get_normalized_data(self):
        target = self.get_normalized_target()

        if self.type == DnsRecordType.MX:
            return f"{self.priority} {target}"

        if self.type == DnsRecordType.SRV:
            return f"{self.priority} {self.weight} {self.port} {target}"

        return target

    def __str__(self):
        data = self.get_normalized_data()

        if self.ttl == 0:
            return f"{self.host} IN {self.raw_type} {data}"
        else:
            return f"{self.host} {self.ttl} IN {self.raw_type} {data}"

    def update(self, record):
        data = Record.get_request_info(record)

        response = StaticApi.put(f"domains/{self.zone.id}/records/{self.id}", data=data)

        self.__set_data(response)

    def delete(self):
        StaticApi.delete(f"domains/{self.zone.id}/records/{self.id}")
        self.zone.records.remove(self)

    @classmethod
    def get_request_info(cls, dns_record, linode_record=None):
        if dns_record.type not in cls.valid_record_types:
            return None

        data = {
            "type": f"{linode_record and linode_record.type or dns_record.type}",
            "name": linode_record and linode_record.host or dns_record.host,
            "ttl_sec": dns_record and dns_record.ttl and dns_record.ttl.seconds or linode_record and linode_record.ttl,
            "target": None,
            "priority": 0,
            "weight": 0,
            "port": 0,
            "service": None,
            "protocol": None,
            "tag": None
        }

        if data["name"] == "@":
            data["name"] = ""

        if dns_record.type == DnsRecordType.SRV:
            data["priority"] = dns_record.data.priority
            data["weight"] = dns_record.data.weight
            data["port"] = dns_record.data.port
            data["target"] = dns_record.data.target.rstrip(".") or "."
            data["service"], data["protocol"] = (x.rstrip("_") for x in data["name"].split(".")[:2])
        elif dns_record.type == DnsRecordType.MX:
            data["priority"] = dns_record.data.priority
            data["target"] = dns_record.data.target.rstrip(".") or "."
        elif dns_record.type == DnsRecordType.CNAME:
            data["target"] = dns_record.data.target.rstrip(".") or "."
        elif dns_record.type == DnsRecordType.TXT:
            data["target"] = dns_record.data.data
        else:
            data["target"] = f"{dns_record.data}"

        return data
