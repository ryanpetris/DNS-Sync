#!/usr/bin/env python3

from .api import StaticApi
from .record import Record
from .zone import Zone
from common import DnsRecordType
from typing import Union, List
from zonebase import Provider as BaseProvider


class Provider(BaseProvider):
    @property
    def id(self) -> str:
        return "cloudflare"

    @property
    def zones(self):
        if self.__zones is None:
            zones = StaticApi.get("zones")

            self.__zones = [Zone(zone) for zone in zones]

        return self.__zones

    def __init__(self):
        self.__zones = None

    def list_zones(self) -> List[str]:
        return [zone.domain for zone in self.zones]

    def get_zone(self, zone: str) -> Union[Zone, None]:
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

    def create_record(self, zone: str, record: Record) -> Record:
        z = self.get_zone(zone)

        for _ in z.records:
            # this is just to ensure records are loaded
            pass

        cf_record = {
            "name": record.host,
            "type": f"{record.type}",
            "content": record.data.normalized,
            "ttl": record and record.ttl and record.ttl.seconds or 1,
            "proxied": False
        }

        if record.type == DnsRecordType.SRV:
            name_parts = record.host.split(".")

            cf_service, cf_proto = name_parts[:2]
            cf_name = ".".join(name_parts[2:]) or "@"

            cf_record = {
                "type": "SRV",
                "ttl": record and record.ttl and record.ttl.seconds or 1,
                "data": {
                    "service": cf_service,
                    "proto": cf_proto,
                    "name": cf_name,
                    "priority": record.data.priority,
                    "weight": record.data.weight,
                    "port": record.data.port,
                    "target": record.data.target
                },
                "proxied": False
            }

        response = StaticApi.post(f"zones/{z.id}/dns_records", data=cf_record)
        record = Record(response)

        z.records.append(record)

        return record

    def update_record(self, zone: str, record: Record, new_record: Record) -> Record:
        z = self.get_zone(zone)

        cf_record = {
            "name": record.host,
            "type": f"{record.type}",
            "content": new_record.data.normalized,
            "ttl": new_record and new_record.ttl and new_record.ttl.seconds or 1
        }

        if record.type == DnsRecordType.SRV:
            name_parts = record.host.split(".")

            cf_service, cf_proto = name_parts[:2]
            cf_name = ".".join(name_parts[2:]) or "@"

            cf_record = {
                "type": "SRV",
                "ttl": new_record and new_record.ttl and new_record.ttl.seconds or 1,
                "data": {
                    "service": cf_service,
                    "proto": cf_proto,
                    "name": cf_name,
                    "priority": new_record.data.priority,
                    "weight": new_record.data.weight,
                    "port": new_record.data.port,
                    "target": new_record.data.target
                }
            }

        response = StaticApi.put(f"zones/{z.id}/dns_records/{record.id}", data=cf_record)

        record.set_data(response)

        return record

    def delete_record(self, zone: str, record: Record):
        z = self.get_zone(zone)

        StaticApi.delete(f"zones/{z.id}/dns_records/{record.id}")

        z.records.remove(record)