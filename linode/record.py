#!/usr/bin/env python3

from __future__ import annotations

from .record_data import RecordData
from common import DnsRecordType, Time
from typing import Union
from zonebase import Record as BaseRecord


class Record(BaseRecord):
    @property
    def host(self) -> Union[str, None]:
        return self.__host

    @property
    def ttl(self) -> Union[Time, None]:
        return self.__ttl

    @property
    def type(self) -> Union[DnsRecordType, None]:
        return self.__type

    @property
    def service(self) -> Union[str, None]:
        if self.type == DnsRecordType.SRV:
            return self.get_service_from_host(self.host)

        return None

    @property
    def protocol(self) -> Union[str, None]:
        if self.type == DnsRecordType.SRV:
            return self.get_protocol_from_host(self.host)

        return None

    @property
    def data(self) -> Union[RecordData, None]:
        return self.__data

    def __init__(self, data):
        self.__host = BaseRecord.normalize_host(data["name"])
        self.__type = BaseRecord.normalize_type(data["type"])
        self.__ttl = BaseRecord.normalize_ttl(None)
        self.__data = RecordData(self.type)

        self.id = None
        self.set_data(data)

    def __str__(self):
        if self.ttl is None:
            return f"{self.host} IN {self.type} {self.data}"
        else:
            return f"{self.host} {self.ttl} IN {self.type} {self.data}"

    def set_data(self, data):
        self.id = data["id"]
        self.__ttl = BaseRecord.normalize_ttl(data["ttl_sec"] or None)

        self.__data.set_data(data)

    @staticmethod
    def get_service_from_host(host: Union[str, None]):
        return host.split(".")[0].lstrip("_")

    @staticmethod
    def get_protocol_from_host(host: Union[str, None]):
        return host.split(".")[1].lstrip("_")
