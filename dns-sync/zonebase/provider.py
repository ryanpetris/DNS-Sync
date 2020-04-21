#!/usr/bin/env python3

from __future__ import annotations

import importlib
import os

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
    @abstractmethod
    def description(self) -> str:
        pass

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

    @staticmethod
    def get_all() -> List[Provider]:
        providers_module = importlib.import_module("..providers", package=__package__)
        providers_path = providers_module.__path__[0]
        providers: List[Provider] = []

        for module_name in os.listdir(providers_path):
            module_path = os.path.join(providers_path, module_name)

            if not os.path.isdir(module_path):
                continue

            try:
                module = importlib.import_module(f"..providers.{module_name}", package=__package__)

                providers.append(module.Provider())
            except:
                pass

        return providers


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
