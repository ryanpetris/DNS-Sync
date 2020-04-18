#!/usr/bin/env python3

from __future__ import annotations

from .api import StaticApi
from .record import Record
from typing import List
from zonebase import Zone as BaseZone


class Zone(BaseZone):
    @property
    def records(self) -> List[Record]:
        if self.__records is None:
            records = StaticApi.get(f"domains/{self.id}/records")
            self.__records = [Record(r) for r in records]

        return self.__records

    @records.setter
    def records(self, value: List[Record]):
        pass

    def __init__(self, zoneinfo):
        super().__init__()

        self.id = zoneinfo["id"]
        self.domain = BaseZone.normalize_domain(zoneinfo["domain"])
        self.soa_email = zoneinfo["soa_email"]
        self.__records = None

