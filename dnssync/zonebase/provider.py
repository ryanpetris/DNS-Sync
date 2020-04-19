#!/usr/bin/env python3

from .record import Record
from .zone import Zone
from ..common import DnsRecordType
from abc import ABC, abstractmethod
from typing import List, Union


class Provider(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    def read_only(self) -> bool:
        return False

    @abstractmethod
    def list_zones(self) -> List[str]:
        pass

    @abstractmethod
    def get_zone(self, zone: str) -> Union[Zone, None]:
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
