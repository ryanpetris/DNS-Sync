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
        return "digitalocean"

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

        data = self.__get_request_info(record)
        response = StaticApi.post(f"domains/{z.domain}/records", data=data)
        record = Record(response)

        z.records.append(record)

        return record

    def update_record(self, zone: str, record: Record, new_record: BaseRecord) -> Record:
        z = self.get_zone(zone)
        data = self.__get_request_info(new_record, record)
        response = StaticApi.put(f"domains/{z.domain}/records/{record.id}", data=data)

        record.set_data(response)

        return record

    def delete_record(self, zone: str, record: Record):
        z = self.get_zone(zone)

        StaticApi.delete(f"domains/{z.domain}/records/{record.id}")

        z.records.remove(record)

    @staticmethod
    def __get_request_info(dns_record, do_record=None):
        data = {
            "type": f"{do_record and do_record.type or dns_record.type}",
            "name": do_record and do_record.host or dns_record.host,
            "ttl": dns_record and dns_record.ttl and dns_record.ttl.seconds or do_record and do_record.ttl,
            "data": dns_record.data.target if dns_record.data.target else None,
            "priority": dns_record.data.priority,
            "weight": dns_record.data.weight,
            "port": dns_record.data.port,
            "tag": None
        }

        if dns_record.type == DnsRecordType.TXT:
            data["data"] = dns_record.data.normalized

        if data["data"] is None:
            data["data"] = f"{dns_record.data}"

        return data
