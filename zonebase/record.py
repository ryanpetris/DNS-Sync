#!/usr/bin/env python3

from .record_data import RecordData
from abc import ABC, abstractmethod
from common import DnsRecordType, Time
from typing import Union


class Record(ABC):
    @property
    @abstractmethod
    def host(self) -> Union[str, None]:
        pass

    @property
    @abstractmethod
    def ttl(self) -> Union[Time, None]:
        pass

    @property
    def serialize_ttl(self) -> bool:
        return self.ttl is not None

    @property
    @abstractmethod
    def type(self) -> Union[DnsRecordType, None]:
        pass

    @property
    @abstractmethod
    def data(self) -> Union[RecordData, None]:
        pass

    def __str__(self):
        host = self.normalize_host(self.host)
        ttl = self.normalize_ttl(self.ttl)
        record_type = self.normalize_type(self.type)

        if ttl is not None:
            return f"{host} {ttl} IN {record_type} {self.data}"
        else:
            return f"{host} IN {record_type} {self.data}"

    @staticmethod
    def normalize_host(host: Union[str, None]) -> str:
        return host or "@"

    @staticmethod
    def normalize_ttl(ttl: Union[Time, int, str, None]) -> Union[Time, None]:
        if ttl is None:
            return None

        return Time(ttl)

    @staticmethod
    def normalize_type(record_type: Union[DnsRecordType, str, None]) -> Union[DnsRecordType, None]:
        if record_type is None:
            return None

        if isinstance(record_type, str):
            return DnsRecordType.parse(record_type)

        if isinstance(record_type, DnsRecordType):
            return record_type

        raise ValueError("record_type must be of type DnsRecordType, str, or None")
