#!/usr/bin/env python3

import re

from .record_data import RecordData, UnparsedRecordData
from ..common import DnsRecordType, Time
from typing import Optional, Union


class Record:
    @property
    def raw(self) -> str:
        host = self.normalize_host(self.host)
        ttl = self.normalize_ttl(self.ttl)
        record_type = self.normalize_type(self.type)

        if ttl is not None:
            return f"{host} {ttl} IN {record_type} {self.data}"
        else:
            return f"{host} IN {record_type} {self.data}"

    @raw.setter
    def raw(self, value: str):
        if not value:
            self.host = self.normalize_host(None)
            self.ttl = self.normalize_ttl(None)
            self.type = self.normalize_type(None)
            self.data = None

        match = re.match("^(?P<host>[^\\s]+)\\s+((?P<ttl>[^\\s]+)\\s+)??IN\\s+(?P<type>[A-Za-z]+)\\s+(?P<data>.*)$", value)

        self.host = match.group("host")
        self.ttl = match.group("ttl")
        self.type = match.group("type")
        self.data = match.group("data")

    @property
    def host(self) -> Optional[str]:
        return self.__host

    @host.setter
    def host(self, value: Optional[str]):
        self.__host = self.normalize_host(value)

    @property
    def ttl(self) -> Optional[Time]:
        return self.__ttl

    @ttl.setter
    def ttl(self, value: Optional[Time]):
        self.__ttl = self.normalize_ttl(value)

    @property
    def serialize_ttl(self) -> bool:
        return self.ttl is not None

    @property
    def type(self) -> Optional[DnsRecordType]:
        return self.__type

    @type.setter
    def type(self, value: Optional[DnsRecordType]):
        self.__type = self.normalize_type(value)
        self.data = self.data

    @property
    def data(self) -> Optional[RecordData]:
        return self.__data

    @data.setter
    def data(self, value: Optional[RecordData]):
        self.__data = self.normalize_data(value, self.type)

    def __init__(self):
        self.__host: Optional[str] = self.normalize_host(None)
        self.__ttl: Optional[Time] = self.normalize_ttl(None)
        self.__type: Optional[DnsRecordType] = self.normalize_type(None)
        self.__data: Optional[RecordData] = None

    def __str__(self):
        return self.raw

    def compare_ttl(self, record: 'Record') -> bool:
        return self.ttl == record.ttl

    @staticmethod
    def normalize_host(host: Optional[str]) -> str:
        return host or "@"

    @staticmethod
    def normalize_ttl(ttl: Union[Time, int, str, None]) -> Optional[Time]:
        if ttl is None:
            return None

        return Time(ttl)

    @staticmethod
    def normalize_type(record_type: Union[DnsRecordType, str, None]) -> Optional[DnsRecordType]:
        if record_type is None:
            return None

        if isinstance(record_type, str):
            return DnsRecordType.parse(record_type)

        if isinstance(record_type, DnsRecordType):
            return record_type

        raise ValueError("record_type must be of type DnsRecordType, str, or None")

    @staticmethod
    def normalize_data(data: Union[RecordData, str, None], record_type: Optional[DnsRecordType] = None) -> Optional[RecordData]:
        if data is None and record_type is None:
            return None

        if record_type is None:
            data_type = UnparsedRecordData
        else:
            data_type = RecordData.get_class_for_type(record_type)

        if issubclass(type(data), data_type):
            return data

        data_instance = data_type()

        if data is not None:
            data_str = f"{data}"

            try:
                data_instance.raw = data_str
            except:
                data_instance = UnparsedRecordData()
                data_instance.raw = data_str

        return data_instance
