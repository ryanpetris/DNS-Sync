#!/usr/bin/env python3

from abc import ABC
from common import DnsRecordType
from ipaddress import IPv4Address, IPv6Address
from typing import Union
from zonebase import RecordData as BaseRecordData, UnparsedRecordData as BaseUnparsedRecordData, IpRecordData as BaseIpRecordData, MxRecordData as BaseMxRecordData, SrvRecordData as BaseSrvRecordData, CnameRecordData as BaseCnameRecordData, TxtRecordData as BaseTxtRecordData


class RecordData(BaseRecordData, ABC):
    @classmethod
    def parse(cls, data: str = None, record_type: DnsRecordType = None):
        base_type = cls.get_class_for_type(record_type)

        for actual_type in (IpRecordData, MxRecordData, SrvRecordData, CnameRecordData, TxtRecordData, UnparsedRecordData):
            if issubclass(actual_type, base_type):
                break

        return actual_type(data)


class UnparsedRecordData(BaseUnparsedRecordData, RecordData):
    @property
    def raw(self) -> str:
        return self.__data

    @raw.setter
    def raw(self, value: Union[str, None]):
        self.__data = value or ""

    def __init__(self, data: Union[str, None] = None):
        self.__data = ""

        parsed = self.parse(data)

        self.raw = parsed.raw


class IpRecordData(BaseIpRecordData, RecordData):
    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        return self.__ip_address

    @ip_address.setter
    def ip_address(self, value: Union[IPv6Address, IPv4Address, None]):
        self.__ip_address = value

    def __init__(self, data: Union[str, None] = None):
        self.__ip_address = None

        parsed = self.parse(data)

        self.ip_address = parsed.ip_address


class MxRecordData(BaseMxRecordData, RecordData):
    @property
    def priority(self) -> Union[int, None]:
        return self.__priority

    @priority.setter
    def priority(self, value: Union[int, None]):
        self.__priority = BaseMxRecordData.normalize_priority(value)

    @property
    def target(self) -> Union[str, None]:
        return self.__target

    @target.setter
    def target(self, value: Union[str, None]):
        self.__target = BaseMxRecordData.normalize_target(value)

    def __init__(self, data: Union[str, None] = None):
        self.__priority = self.normalize_priority(None)
        self.__target = self.normalize_target(None)

        parsed = self.parse(data)

        self.priority = parsed.priority
        self.target = parsed.target


class SrvRecordData(BaseSrvRecordData, RecordData):
    @property
    def priority(self) -> Union[int, None]:
        return self.__priority

    @priority.setter
    def priority(self, value: Union[int, None]):
        self.__priority = self.normalize_priority(value)

    @property
    def weight(self) -> Union[int, None]:
        return self.__weight

    @weight.setter
    def weight(self, value: Union[int, None]):
        self.__weight = self.normalize_weight(value)

    @property
    def port(self) -> Union[int, None]:
        return self.__port

    @port.setter
    def port(self, value: Union[int, None]):
        self.__port = self.normalize_port(value)

    @property
    def target(self) -> Union[str, None]:
        return self.__target

    @target.setter
    def target(self, value: Union[str, None]):
        self.__target = self.normalize_target(value)

    def __init__(self, data: Union[str, None] = None):
        self.__priority = self.normalize_priority(None)
        self.__weight = self.normalize_weight(None)
        self.__port = self.normalize_port(None)
        self.__target = self.normalize_target(None)

        parsed = self.parse(data)

        self.priority = parsed.priority
        self.weight = parsed.weight
        self.port = parsed.port
        self.target = parsed.target


class CnameRecordData(BaseCnameRecordData, RecordData):
    @property
    def target(self) -> Union[str, None]:
        return self.__target

    @target.setter
    def target(self, value: Union[str, None]):
        self.__target = self.normalize_target(value)

    def __init__(self, data: Union[str, None] = None):
        self.__target = self.normalize_target(None)

        parsed = self.parse(data)

        self.target = parsed.target


class TxtRecordData(BaseTxtRecordData, RecordData):
    @property
    def normalized(self) -> str:
        return self.__normalized

    @normalized.setter
    def normalized(self, data: Union[str, None]):
        self.__normalized = data
        self.__raw = None

    @property
    def raw(self) -> str:
        if self.__raw is None:
            self.__raw = self.quote_data(self.__normalized)

        return self.__raw

    @raw.setter
    def raw(self, data: Union[str, None]):
        self.normalized = self.unqoute_data(data)

    def __init__(self, data: Union[str, None] = None):
        self.__normalized = None
        self.__raw = None

        self.raw = data
