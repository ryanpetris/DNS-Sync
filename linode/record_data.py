#!/usr/bin/env python3

from common import DnsRecordType
from ipaddress import IPv4Address, IPv6Address
from typing import Union
from zonebase import RecordData as BaseRecordData, CnameRecordData as BaseCnameRecordData, MxRecordData as BaseMxRecordData, SrvRecordData as BaseSrvRecordData, IpRecordData as BaseIpRecordData, TxtRecordData as BaseTxtRecordData

class RecordData(BaseRecordData):
    @property
    def raw(self) -> str:
        if self.type == DnsRecordType.SRV:
            return f"{self.priority} {self.weight} {self.port} {self.target}"

        if self.type == DnsRecordType.MX:
            return f"{self.priority} {self.target}"

        if self.type in (DnsRecordType.A, DnsRecordType.AAAA):
            return f"{self.ip_address.compressed}"

        if self.type == DnsRecordType.TXT:
            return BaseTxtRecordData.quote_data(self.__target)

        return self.target

    @property
    def normalized(self) -> str:
        if self.type == DnsRecordType.TXT:
            return self.__target

        return self.raw

    @property
    def priority(self) -> Union[int, None]:
        if self.type == DnsRecordType.SRV:
            return BaseSrvRecordData.normalize_priority(self.__priority)

        if self.type == DnsRecordType.MX:
            return BaseMxRecordData.normalize_priority(self.__priority)

        return None

    @property
    def weight(self) -> Union[int, None]:
        if self.type == DnsRecordType.SRV:
            return BaseSrvRecordData.normalize_weight(self.__weight)

        return None

    @property
    def port(self) -> Union[int, None]:
        if self.type == DnsRecordType.SRV:
            return BaseSrvRecordData.normalize_port(self.__port)

        return None

    @property
    def target(self) -> Union[str, None]:
        if self.type == DnsRecordType.SRV:
            return BaseSrvRecordData.normalize_target(self.__target)

        if self.type == DnsRecordType.MX:
            return BaseMxRecordData.normalize_target(self.__target)

        if self.type == DnsRecordType.CNAME:
            return BaseCnameRecordData.normalize_target(self.__target)

        return None

    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        if self.type in [DnsRecordType.A, DnsRecordType.AAAA]:
            return BaseIpRecordData.parse(self.__target).ip_address

        return None

    def __init__(self, record_type: DnsRecordType):
        self.type = record_type

        self.__priority = None
        self.__weight = None
        self.__port = None
        self.__target = None

    def set_data(self, data):
        self.__priority = data["priority"]
        self.__weight = data["weight"]
        self.__port = data["port"]
        self.__target = data["target"]
