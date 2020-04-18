#!/usr/bin/env python3

from __future__ import annotations

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
        self.id = zoneinfo["id"]
        self.__domain = BaseZone.normalize_domain(zoneinfo["domain"])
        self.soa_email = zoneinfo["soa_email"]
        self.__records = None

    def __fetch_records(self):
        if self.__records is not None:
            return

        records = StaticApi.get(f"domains/{self.id}/records")
        self.__records = [Record(r) for r in records]

