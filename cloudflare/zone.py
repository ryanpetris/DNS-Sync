#!/usr/bin/env python3

from .api import StaticApi
from .record import Record
from typing import List, Union
from zonebase import Zone as BaseZone


class Zone(BaseZone):
    @property
    def domain(self) -> Union[str, None]:
        return self.__domain

    @property
    def records(self) -> List[Record]:
        if self.__records is None:
            self.__fetch_records()

        return self.__records

    def __init__(self, zoneinfo):
        self.__domain = zoneinfo["name"]
        self.__records = None

        self.id = zoneinfo["id"]
        self.nameservers = zoneinfo["name_servers"]

    def __fetch_records(self):
        if self.__records is not None:
            return

        records = StaticApi.get(f"zones/{self.id}/dns_records")
        self.__records = [Record(r) for r in records]
