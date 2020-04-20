#!/usr/bin/env python3

from __future__ import annotations

import re

from ..common import DnsRecordType
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Type, Optional, Union


class RecordData:
    @property
    def raw(self) -> str:
        return self.__raw

    @raw.setter
    def raw(self, value: str):
        self.__raw = value or ""

    @property
    def normalized(self) -> str:
        return self.raw

    @normalized.setter
    def normalized(self, value: str):
        self.raw = value

    @property
    def priority(self) -> Optional[int]:
        return None

    @priority.setter
    def priority(self, value: Optional[int]):
        pass

    @property
    def weight(self) -> Optional[int]:
        return None

    @weight.setter
    def weight(self, value: Optional[int]):
        pass

    @property
    def port(self) -> Optional[int]:
        return None

    @port.setter
    def port(self, value: Optional[int]):
        pass

    @property
    def target(self) -> Optional[str]:
        return None

    @target.setter
    def target(self, value: Optional[str]):
        pass

    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        return None

    @ip_address.setter
    def ip_address(self, value: Union[IPv6Address, IPv4Address, None]):
        pass

    def __init__(self):
        self.__raw: str = ""

    def __str__(self) -> str:
        return self.raw or ""

    def __eq__(self, other):
        if not issubclass(type(other), RecordData):
            return False

        return (self.raw or "") == (other.raw or "")

    def __lt__(self, other):
        if not issubclass(type(other), RecordData):
            return False

        return (self.raw or "") < (other.raw or "")

    def __gt__(self, other):
        if not issubclass(type(other), RecordData):
            return False

        return (self.raw or "") > (other.raw or "")

    @staticmethod
    def get_class_for_type(rtype: DnsRecordType) -> Type[RecordData]:
        if rtype in (DnsRecordType.A, DnsRecordType.AAAA):
            return IpRecordData

        if rtype == DnsRecordType.MX:
            return MxRecordData

        if rtype == DnsRecordType.SRV:
            return SrvRecordData

        if rtype == DnsRecordType.CNAME:
            return CnameRecordData

        if rtype in (DnsRecordType.TXT, DnsRecordType.SPF):
            return TxtRecordData

        return UnparsedRecordData

    @classmethod
    def type_parse(cls, rtype: DnsRecordType, data: Optional[str]) -> RecordData:
        rclass = cls.get_class_for_type(rtype)

        result = rclass()
        result.raw = data

        return result


class UnparsedRecordData(RecordData):
    def __init__(self):
        super().__init__()

    @staticmethod
    def parse(data: Optional[str]) -> UnparsedRecordData:
        result = UnparsedRecordData()
        result.raw = data

        return result


class IpRecordData(RecordData):
    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        return self.__ip_address

    @ip_address.setter
    def ip_address(self, value: Union[IPv6Address, IPv4Address, None]):
        self.__ip_address = self.normalize_ip_address(value)

    @property
    def raw(self) -> str:
        if self.ip_address is None:
            return ""

        return self.ip_address.compressed

    @raw.setter
    def raw(self, value: str):
        self.ip_address = self.normalize_ip_address(value)

    def __init__(self):
        super().__init__()

        self.__ip_address: Union[IPv6Address, IPv4Address, None] = self.normalize_ip_address(None)

    @staticmethod
    def normalize_ip_address(ip: Union[IPv6Address, IPv4Address, str, None]):
        if issubclass(type(ip), IPv6Address) or issubclass(type(ip), IPv4Address):
            return ip

        if ip is None:
            return None

        try:
            return ip_address(ip.strip())
        except:
            raise ValueError(f"{ip} is an invalid IP address")


class MxRecordData(RecordData):
    @property
    def priority(self) -> Optional[int]:
        return self.__priority

    @priority.setter
    def priority(self, value: Optional[int]):
        self.__priority = self.normalize_priority(value)

    @property
    def target(self) -> Optional[str]:
        return self.__target

    @target.setter
    def target(self, value: Optional[str]):
        self.__target = self.normalize_target(value)

    @property
    def raw(self) -> str:
        return f"{self.priority} {self.target}"

    @raw.setter
    def raw(self, value: str):
        if not value:
            self.priority = None
            self.target = None
            return

        match = re.match("^(?P<priority>[0-9]+)\\s+(?P<target>[^\\s]+)$", value.strip())

        if not match:
            raise ValueError(f"Invalid MX record data: {value}")

        self.priority = int(match.group("priority"))
        self.target = match.group("target")

    def __init__(self):
        super().__init__()

        self.__priority: Optional[int] = self.normalize_priority(None)
        self.__target: Optional[str] = self.normalize_target(None)

    @staticmethod
    def normalize_priority(priority: Optional[int]) -> int:
        return priority or 0

    @staticmethod
    def normalize_target(target: Optional[str]) -> str:
        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class SrvRecordData(RecordData):
    @property
    def priority(self) -> Optional[int]:
        return self.__priority

    @priority.setter
    def priority(self, value: Optional[int]):
        self.__priority = self.normalize_priority(value)

    @property
    def weight(self) -> Optional[int]:
        return self.__weight

    @weight.setter
    def weight(self, value: Optional[int]):
        self.__weight = self.normalize_weight(value)

    @property
    def port(self) -> Optional[int]:
        return self.__port

    @port.setter
    def port(self, value: Optional[int]):
        self.__port = self.normalize_port(value)

    @property
    def target(self) -> Optional[str]:
        return self.__target

    @target.setter
    def target(self, value: Optional[str]):
        self.__target = self.normalize_target(value)

    @property
    def raw(self) -> str:
        priority = self.normalize_priority(self.priority)
        weight = self.normalize_weight(self.weight)
        port = self.normalize_port(self.port)
        target = self.normalize_target(self.target)

        return f"{priority} {weight} {port} {target}"

    @raw.setter
    def raw(self, value: str):
        if not value:
            self.priority = None
            self.weight = None
            self.port = None
            self.target = None
            return

        match = re.match("^(?P<priority>[0-9]+)\\s+(?P<weight>[0-9]+)\\s+(?P<port>[0-9]+)\\s+(?P<target>[^\\s]+)$", value.strip())

        if not match:
            raise ValueError(f"Invalid SRV record data: {value}")

        self.priority = int(match.group("priority"))
        self.weight = int(match.group("weight"))
        self.port = int(match.group("port"))
        self.target = match.group("target")

    def __init__(self):
        super().__init__()

        self.__priority: Optional[int] = self.normalize_priority(None)
        self.__weight: Optional[int] = self.normalize_weight(None)
        self.__port: Optional[int] = self.normalize_port(None)
        self.__target: Optional[str] = self.normalize_target(None)

    @staticmethod
    def normalize_priority(priority: Optional[int]) -> int:
        return priority or 0

    @staticmethod
    def normalize_weight(weight: Optional[int]) -> int:
        return weight or 0

    @staticmethod
    def normalize_port(port: Optional[int]) -> int:
        return port or 0

    @staticmethod
    def normalize_target(target: Optional[str]) -> str:
        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class CnameRecordData(RecordData):
    @property
    def target(self) -> Optional[str]:
        return self.__target

    @target.setter
    def target(self, value: Optional[str]):
        self.__target = self.normalize_target(value)

    @property
    def raw(self) -> str:
        return self.target

    @raw.setter
    def raw(self, value: str):
        self.target = value

    def __init__(self):
        super().__init__()

        self.__target = self.normalize_target(None)

    @staticmethod
    def normalize_target(target: Optional[str]) -> str:
        if re.match("\\s", target or ""):
            raise ValueError("CNAME data field should not contain whitespace")

        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class TxtRecordData(RecordData):
    @property
    def normalized(self) -> str:
        return self.__normalized

    @normalized.setter
    def normalized(self, value: str):
        self.__normalized = value or ""

    @property
    def raw(self) -> str:
        return self.quote_data(self.normalized)

    @raw.setter
    def raw(self, value: str):
        self.normalized = self.unqoute_data(value)

    def __init__(self):
        super().__init__()

        self.__normalized: str = ""

    @staticmethod
    def unqoute_data(data: Optional[str] = None) -> str:
        whitespace_char_regex = re.compile("^\\s$")
        escape_char = "\\"
        quote_char = '"'

        if not data:
            return ""

        data.strip()

        is_open = False
        is_escape = False
        part = ""
        result = ""

        for char in data:
            if not is_open:
                if whitespace_char_regex.match(char):
                    continue

                if char == quote_char:
                    is_open = True
                    continue

                raise ValueError(f"Invalid character found outside of TXT value: {char}")

            if is_escape:
                part += char
                is_escape = False
                continue

            if char == escape_char:
                is_escape = True
                continue

            if char == quote_char:
                result += part
                part = ""
                is_open = False

                continue

            part += char

        return result

    @staticmethod
    def quote_data(data: Optional[str] = None) -> str:
        escape_char = "\\"
        quote_char = '"'
        chars_to_escape = "\\\";"

        result = quote_char

        if data:
            for char in data:
                if char in chars_to_escape:
                    result += escape_char

                result += char

        result += quote_char

        return result
