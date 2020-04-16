#!/usr/bin/env python3

import re

from .record_data import RecordData
from .record_type import RecordType
from .util import Time


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


class Record:
    record_regex = re.compile("^(?P<host>[^\\s]+)\\s+((?P<ttl>[^\\s]+)\\s+)??IN\\s+(?P<type>[A-Za-z]+)\\s+(?P<data>.*)$")

    def __init__(self, data=None, defaults=None):
        self.host = ""
        self.has_ttl = True
        self.ttl = None
        self.type = None
        self.data = None

        match = self.__class__.record_regex.match(data)

        if not match:
            raise ValueError("Invalid record data")

        self.host = match.group("host")

        self.type = RecordType.parse(match.group("type"))
        self.data = RecordData.parse(match.group("data"), self.type)
        self.has_ttl = match.group("ttl") is not None

        if self.has_ttl:
            self.ttl = Time(match.group("ttl"))
        elif defaults:
            self.ttl = defaults.ttl

    def __str__(self):
        if self.has_ttl:
            return f"{self.host} {self.ttl} IN {self.type} {self.data}"
        else:
            return f"{self.host} IN {self.type} {self.data}"
