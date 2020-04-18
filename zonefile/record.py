#!/usr/bin/env python3

import re

from .record_data import RecordData
from common import DnsRecordType, Time
from typing import Union
from zonebase import Record as BaseRecord


class RecordDefaults:
    def __init__(self, lines=None):
        self.ttl = None

        if not lines:
            return

        for line in lines:
            if line.startswith("$TTL"):
                parts = line.split(" ")

                if len(parts) < 2:
                    continue

                self.ttl = Time(parts[1])

    def __str__(self):
        parts = []

        if self.ttl is not None:
            parts.append(f"$TTL {self.ttl}")

        return "\n".join(parts)


class Record(BaseRecord):
    __record_regex = re.compile("^(?P<host>[^\\s]+)\\s+((?P<ttl>[^\\s]+)\\s+)??IN\\s+(?P<type>[A-Za-z]+)\\s+(?P<data>.*)$")

    @property
    def host(self) -> Union[str, None]:
        return self.__host

    @host.setter
    def host(self, value: Union[str, None]):
        self.__host = BaseRecord.normalize_host(value)

    @property
    def ttl(self) -> Union[Time, None]:
        return self.__ttl

    @ttl.setter
    def ttl(self, value: Union[Time, None]):
        self.__ttl = BaseRecord.normalize_ttl(value)

    @property
    def serialize_ttl(self) -> bool:
        return self.has_ttl

    @property
    def type(self) -> Union[DnsRecordType, None]:
        return self.__type

    @type.setter
    def type(self, value: Union[DnsRecordType, None]):
        self.__type = BaseRecord.normalize_type(value)

    @property
    def data(self) -> Union[RecordData, None]:
        return self.__data

    @data.setter
    def data(self, value: Union[RecordData, None]):
        self.__data = value

    def __init__(self, data=None, defaults=None):
        self.__host = BaseRecord.normalize_host(None)
        self.has_ttl = False
        self.__ttl = BaseRecord.normalize_ttl(None)
        self.__type = BaseRecord.normalize_type(None)
        self.__data = None

        match = self.__record_regex.match(data)

        if not match:
            raise ValueError("Invalid record data")

        self.host = match.group("host")

        self.type = DnsRecordType.parse(match.group("type"))
        self.data = RecordData.parse(match.group("data"), self.type)
        self.has_ttl = match.group("ttl") is not None

        if self.has_ttl:
            self.ttl = match.group("ttl")
        elif defaults:
            self.ttl = defaults.ttl

    def __str__(self):
        if self.has_ttl:
            return f"{self.host} {self.ttl} IN {self.type} {self.data}"
        else:
            return f"{self.host} IN {self.type} {self.data}"
