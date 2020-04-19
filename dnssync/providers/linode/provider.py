#!/usr/bin/env python3

from .api import StaticApi
from .zone import Zone
from .record import Record
from ...common import DnsRecordType
from ...zonebase import Provider as BaseProvider, Record as BaseRecord
from typing import List, Union


class Provider(BaseProvider):
    @property
    def id(self) -> str:
        return "linode"

    @property
    def zones(self):
        if self.__zones is None:
            zones = StaticApi.get("domains")

            self.__zones = [Zone(zone) for zone in zones]

        return self.__zones

    def __init__(self):
        self.__zones = None

    def list_zones(self) -> List[str]:
        return [zone.domain for zone in self.zones]

    def get_zone(self, zone: str) -> Union[Zone, None]:
        return next((z for z in self.zones if z.domain == zone), None)

    def can_read_type(self, rtype: DnsRecordType) -> bool:
        return rtype in [
            DnsRecordType.A,
            DnsRecordType.AAAA,
            DnsRecordType.MX,
            DnsRecordType.SRV,
            DnsRecordType.CNAME,
            DnsRecordType.TXT
        ]

    def can_write_type(self, rtype: DnsRecordType) -> bool:
        return self.can_read_type(rtype)

    def create_record(self, zone: str, record: BaseRecord) -> Record:
        z = self.get_zone(zone)

        for _ in z.records:
            # this is just to ensure records are loaded
            pass

        data = self.__get_request_info(record)
        response = StaticApi.post(f"domains/{z.id}/records", data=data)
        record = Record(response)

        z.records.append(record)

        return record

    def update_record(self, zone: str, record: Record, new_record: BaseRecord) -> Record:
        z = self.get_zone(zone)
        data = self.__get_request_info(new_record, record)
        response = StaticApi.put(f"domains/{z.id}/records/{record.id}", data=data)

        record.set_data(response)

        return record

    def delete_record(self, zone: str, record: Record):
        z = self.get_zone(zone)

        StaticApi.delete(f"domains/{z.id}/records/{record.id}")

        z.records.remove(record)

    @staticmethod
    def __get_request_info(dns_record, linode_record=None):
        data = {
            "type": f"{linode_record and linode_record.type or dns_record.type}",
            "name": linode_record and linode_record.host or dns_record.host,
            "ttl_sec": dns_record and dns_record.ttl and dns_record.ttl.seconds or linode_record and linode_record.ttl,
            "target": (dns_record.data.target.rstrip(".") or ".") if dns_record.data.target else None,
            "priority": dns_record.data.priority or 0,
            "weight": dns_record.data.weight or 0,
            "port": dns_record.data.port or 0,
            "service": None,
            "protocol": None,
            "tag": None
        }

        if data["name"] == "@":
            data["name"] = ""

        if dns_record.type == DnsRecordType.SRV:
            data["service"] = Record.get_service_from_host(data["name"])
            data["protocol"] = Record.get_protocol_from_host(data["name"])

        if dns_record.type == DnsRecordType.TXT:
            data["target"] = dns_record.data.normalized

        if data["target"] is None:
            data["target"] = f"{dns_record.data}"

        return data
