#!/usr/bin/env python3

from .record import Record, RecordDefaults
from typing import List, Union
from zonebase import Zone as BaseZone


class Zone(BaseZone):
    @property
    def domain(self) -> Union[str, None]:
        return self.__domain

    @domain.setter
    def domain(self, value: Union[str, None]):
        self.__domain = BaseZone.normalize_domain(value)

    @property
    def records(self) -> List[Record]:
        return self.__records

    @records.setter
    def records(self, value: Union[List[Record], None]):
        self.__records = value or []

    def __init__(self, data=None, domain=None):
        self.__domain = BaseZone.normalize_domain(None)
        self.__records = []

        self.defaults = None
        self.domain = domain

        record_lines = []
        default_lines = []

        for line in data.split("\n"):
            line = line.replace("\r", "").strip()

            if not line:
                continue

            if line.startswith("$"):
                default_lines.append(line)
            else:
                record_lines.append(line)

        self.defaults = RecordDefaults(default_lines)
        self.records = [Record(line, self.defaults) for line in record_lines]

    def __str__(self) -> str:
        outlines = []

        if self.defaults:
            outlines.append(f"{self.defaults}")

        out = "\n".join(outlines)
        superout = super().__str__()

        if out and superout:
            out += "\n"

        return out + superout
