#!/usr/bin/env python3

from .api import StaticApi
from .record import Record
from typing import List
from zonebase import Zone as BaseZone


class Zone(BaseZone):
    @property
    def records(self) -> List[Record]:
        if self.__records is None:
            records = StaticApi.get(f"zones/{self.id}/dns_records")
            self.__records = [Record(r) for r in records]

        return self.__records

    @records.setter
    def records(self, value: List[Record]):
        pass

    def __init__(self, zoneinfo):
        self.domain = zoneinfo["name"]
        self.id = zoneinfo["id"]
        self.nameservers = zoneinfo["name_servers"]
        self.__records = None
