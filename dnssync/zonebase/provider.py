#!/usr/bin/env python3

from .record import Record
from .zone import Zone
from ..common import DnsRecordType, Time
from abc import ABC, abstractmethod
from typing import List, Optional


class Provider(ABC):
    default_ttl = Time("1h")

    @property
    def id(self) -> str:
        return self.__class__.__module__.split(".")[-2]

    @property
    def read_only(self) -> bool:
        return False

    @abstractmethod
    def list_zones(self) -> List[str]:
        pass

    @abstractmethod
    def get_zone(self, zone: str) -> Optional[Zone]:
        pass

    @abstractmethod
    def can_read_type(self, rtype: DnsRecordType) -> bool:
        pass

    @abstractmethod
    def can_write_type(self, rtype: DnsRecordType) -> bool:
        pass

    @abstractmethod
    def create_record(self, zone: str, record: Record) -> Record:
        pass

    @abstractmethod
    def update_record(self, zone: str, record: Record, new_record: Record) -> Record:
        pass

    @abstractmethod
    def delete_record(self, zone: str, record: Record):
        pass

    def find_record_ttl(self, *args: Optional[Record], default: int = None) -> int:
        for record in args:
            if record and record.ttl and record.ttl.seconds:
                return record.ttl.seconds

        if default is not None:
            return default

        return self.default_ttl.seconds


class ReadOnlyProvider(Provider, ABC):
    @property
    def read_only(self) -> bool:
        return True

    def can_write_type(self, rtype: DnsRecordType) -> bool:
        return False

    def create_record(self, zone: str, record: Record) -> Record:
        pass

    def update_record(self, zone: str, record: Record, new_record: Record) -> Record:
        pass

    def delete_record(self, zone: str, record: Record):
        pass


class TransactionProvider(Provider, ABC):
    @abstractmethod
    def commit_zone(self, zone: str):
        pass
