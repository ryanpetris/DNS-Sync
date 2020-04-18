#!/usr/bin/env python3

from common import Time
from zonebase import Record as BaseRecord


class RecordDefaults:
    def __init__(self, lines=None):
        self.ttl = None

        if not lines:
            return

        for line in lines:
            if line.startswith("$TTL"):
                parts = line.split(" ")

                if len(parts) < 2:
                    continue

                self.ttl = Time(parts[1])

    def __str__(self):
        parts = []

        if self.ttl is not None:
            parts.append(f"$TTL {self.ttl}")

        return "\n".join(parts)


class Record(BaseRecord):
    @property
    def serialize_ttl(self) -> bool:
        return self.__has_ttl

    def __init__(self, data=None, defaults=None):
        super().__init__()

        self.__has_ttl: bool = False
        self.raw = data

        if self.ttl is None:
            if defaults:
                self.ttl = defaults.ttl
        else:
            self.__has_ttl = True
