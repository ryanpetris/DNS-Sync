#!/usr/bin/env python3

from .api import StaticApi
from .zone import Zone
from .record import Record
from ...common import DnsRecordType
from ...zonebase import TransactionProvider as BaseTransactionProvider, Record as BaseRecord
from typing import List, Optional


class Provider(BaseTransactionProvider):
    @property
    def description(self) -> str:
        return "GoDaddy sync provider."

    @property
    def zones(self):
        if self.__zones is None:
            params = {
                "statuses": ",".join(["ACTIVE"]),
                "includes": ",".join(["nameServers"])
            }

            zones = StaticApi.get("domains", params=params)

            self.__zones = [Zone(zone) for zone in zones if self.__has_godaddy_nameserver(zone["nameServers"])]

        return self.__zones

    def __init__(self):
        self.__zones = None

    def list_zones(self) -> List[str]:
        return [zone.domain for zone in self.zones]

    def get_zone(self, zone: str) -> Optional[Zone]:
        return next((z for z in self.zones if z.domain == zone), None)

    def can_read_type(self, rtype: DnsRecordType) -> bool:
        return rtype in self.can_write_type(rtype) or rtype in [
            DnsRecordType.NS
        ]

    def can_write_type(self, rtype: DnsRecordType) -> bool:
        return rtype in [
            DnsRecordType.A,
            DnsRecordType.AAAA,
            DnsRecordType.MX,
            DnsRecordType.SRV,
            DnsRecordType.CNAME,
            DnsRecordType.TXT
        ]

    def create_record(self, zone: str, record: BaseRecord) -> Record:
        z = self.get_zone(zone)

        for _ in z.records:
            # this is just to ensure records are loaded
            pass

        new_record = Record(record)

        z.records.append(new_record)

        return record

    def update_record(self, zone: str, record: Record, new_record: BaseRecord) -> Record:
        record.set_data(new_record)
        return record

    def delete_record(self, zone: str, record: Record):
        z = self.get_zone(zone)
        z.records.remove(record)

    def __get_request_info(self, record):
        data = {
            "type": f"{record.type}",
            "name": record.host,
            "ttl": self.find_record_ttl(record),
            "data": record.data.target
        }

        if record.type == DnsRecordType.SRV:
            parts = record.host.split(".")

            data["service"], data["protocol"] = parts[:2]
            data["name"] = ".".join(parts[2:]) or "@"

        if record.type == DnsRecordType.TXT:
            data["data"] = record.data.normalized

        if data["data"] is None:
            data["data"] = f"{record.data}"

        if record.data.priority is not None:
            data["priority"] = record.data.priority

        if record.data.weight is not None:
            data["weight"] = record.data.weight

        if record.data.port is not None:
            data["port"] = record.data.port

        return data

    @staticmethod
    def __has_godaddy_nameserver(nameservers: List[str]) -> bool:
        if not nameservers:
            return False

        return next((ns for ns in nameservers if ns.endswith(".domaincontrol.com")), None) is not None

    def commit_zone(self, zone: str):
        z = self.get_zone(zone)
        data = [self.__get_request_info(r) for r in z.records]

        StaticApi.put(f"domains/{z.domain}/records", data=data)
