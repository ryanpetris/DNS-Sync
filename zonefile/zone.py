#!/usr/bin/env python3

from .record import Record, RecordDefaults
from zonebase import Zone as BaseZone


class Zone(BaseZone):
    def __init__(self, data=None, domain=None):
        super().__init__()

        self.domain = domain
        self.__defaults = None

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

        self.__defaults = RecordDefaults(default_lines)
        self.records = [Record(line, self.__defaults) for line in record_lines]

    def __str__(self) -> str:
        outlines = []

        if self.__defaults:
            outlines.append(f"{self.__defaults}")

        out = "\n".join(outlines)
        superout = super().__str__()

        if out and superout:
            out += "\n"

        return out + superout
