#!/usr/bin/env python3

import inspect
import ipaddress
import re

from .record_type import RecordType
from common import tryit
from typing import Iterator


def record_data_handler(cls):
    if not inspect.isclass(cls):
        return cls

    if not issubclass(cls, RecordData):
        return cls

    for record_type in cls.handles:
        if record_type in RecordData.handlers:
            raise ValueError(f"Handler for {record_type} already registered.")

        RecordData.handlers[record_type] = cls

    return cls


class RecordData:
    handles = []
    handlers = {}

    def __init__(self, data: str = None):
        pass

    def __str__(self) -> str:
        pass

    def get_normalized_data(self) -> str:
        return self.__str__()

    @staticmethod
    def parse(data: str = None, record_type: RecordType = None):
        if not record_type or record_type not in RecordData.handlers:
            return UnparsedRecordData(data)

        return RecordData.handlers[record_type](data)


class UnparsedRecordData(RecordData):
    handles = []

    def __init__(self, data: str = None):
        super().__init__(data)

        self.data = data

    def __str__(self) -> str:
        return self.data


@record_data_handler
class IpRecordData(RecordData):
    handles = [
        RecordType.A,
        RecordType.AAAA
    ]

    def __init__(self, data: str = None):
        super().__init__(data)

        self.ip_address = tryit(ipaddress.ip_address)(data)

    def __str__(self) -> str:
        if self.ip_address is None:
            return ""

        return self.ip_address.compressed


@record_data_handler
class MxRecordData(RecordData):
    handles = [
        RecordType.MX
    ]

    record_regex = re.compile("^(?P<priority>[0-9]+)\\s+(?P<target>[^\\s]+)$")

    def __init__(self, data: str = None):
        super().__init__(data)

        self.priority = None
        self.target = None

        if not data:
            return

        match = self.__class__.record_regex.match(data)

        if not match:
            raise ValueError(f"Invalid MX record data: {data}")

        self.priority = int(match.group("priority"))
        self.target = match.group("target")

        if not self.target.endswith("."):
            self.target = f"{self.target}."

    def __str__(self) -> str:
        if self.priority is None and self.target is None:
            return ""

        return f"{self.priority} {self.target}"


@record_data_handler
class SrvRecordData(RecordData):
    handles = [
        RecordType.SRV
    ]

    record_regex = re.compile("^(?P<priority>[0-9]+)\\s+(?P<weight>[0-9]+)\\s+(?P<port>[0-9]+)\\s+(?P<target>[^\\s]+)$")

    def __init__(self, data: str = None):
        super().__init__(data)

        self.priority = None
        self.weight = None
        self.port = None
        self.target = None

        if not data:
            return

        match = self.__class__.record_regex.match(data)

        if not match:
            raise ValueError(f"Invalid SRV record data: {data}")

        self.priority = int(match.group("priority"))
        self.weight = int(match.group("weight"))
        self.port = int(match.group("port"))
        self.target = match.group("target")

        if not self.target.endswith("."):
            self.target = f"{self.target}."

    def __str__(self) -> str:
        if self.priority is None and self.weight is None and self.port is None and self.target is None:
            return ""

        return f"{self.priority} {self.weight} {self.port} {self.target}"


@record_data_handler
class CnameRecordData(RecordData):
    handles = [
        RecordType.CNAME
    ]

    whitespace_regex = re.compile("\\s")

    def __init__(self, data: str = None):
        super().__init__(data)

        self.target = None

        if not data:
            return

        data = data.strip()

        if self.__class__.whitespace_regex.search(data):
            raise ValueError("CNAME data field should not contain whitespace")

        self.target = data

        if not self.target.endswith("."):
            self.target = f"{self.target}."

    def __str__(self) -> str:
        return self.target or ""


@record_data_handler
class TxtRecordData(RecordData):
    handles = [
        RecordType.TXT,
        RecordType.SPF
    ]

    whitespace_char_regex = re.compile("^\\s$")
    escape_char = "\\"
    quote_char = '"'
    chars_to_escape = "\\\";"

    def __init__(self, data: str = None):
        super().__init__(data)

        self.data = ""

        for part in self.__get_quoted_parts(data):
            self.data += part

    def __str__(self) -> str:
        cls = self.__class__
        data = cls.quote_char

        for char in self.data:
            if char in cls.chars_to_escape:
                data += cls.escape_char

            data += char

        data += cls.quote_char

        return data

    def get_normalized_data(self) -> str:
        return self.data

    def __get_quoted_parts(self, data: str = None) -> Iterator[str]:
        if not data:
            return

        data.strip()

        is_open = False
        is_escape = False
        part = ""
        cls = self.__class__

        for char in data:
            if not is_open:
                if cls.whitespace_char_regex.match(char):
                    continue

                if char == cls.quote_char:
                    is_open = True
                    continue

                raise ValueError(f"Invalid character found outside of TXT value: {char}")

            if is_escape:
                part += char
                is_escape = False
                continue

            if char == cls.escape_char:
                is_escape = True
                continue

            if char == cls.quote_char:
                yield part

                is_open = False
                part = ""

                continue

            part += char
