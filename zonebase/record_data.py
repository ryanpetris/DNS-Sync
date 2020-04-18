#!/usr/bin/env python3

from __future__ import annotations

import re

from abc import ABC, abstractmethod
from common import DnsRecordType
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Type, Union


class RecordData(ABC):
    @property
    @abstractmethod
    def raw(self) -> str:
        pass

    @property
    def normalized(self) -> str:
        return self.raw

    @property
    def priority(self) -> Union[int, None]:
        return None

    @property
    def weight(self) -> Union[int, None]:
        return None

    @property
    def port(self) -> Union[int, None]:
        return None

    @property
    def target(self) -> Union[str, None]:
        return None

    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        return None

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
    def get_class_for_type(rtype: DnsRecordType) -> Type[ParseableRecordData]:
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
    def type_parse(cls, rtype: DnsRecordType, data: Union[str, None]) -> RecordData:
        rclass = cls.get_class_for_type(rtype)

        return rclass.parse(data)


class ParseableRecordData(RecordData, ABC):
    @staticmethod
    @abstractmethod
    def parse(data: Union[str, None]) -> ParseableRecordData:
        pass


class UnparsedRecordData(ParseableRecordData, ABC):
    @staticmethod
    def parse(data: Union[str, None]) -> UnparsedRecordData:
        return UnparsedRecordDataImp(data)


class UnparsedRecordDataImp(UnparsedRecordData):
    @property
    def raw(self) -> str:
        return self.__data

    def __init__(self, data: Union[str, None]):
        self.__data = data


class IpRecordData(ParseableRecordData, ABC):
    @property
    @abstractmethod
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        pass

    @property
    def raw(self) -> str:
        if self.ip_address is None:
            return ""

        return self.ip_address.compressed

    @staticmethod
    def parse(data: Union[str, None]) -> IpRecordData:
        if data is None:
            return IpRecordDataImp()

        try:
            ip = ip_address(data.strip())
        except:
            ip = None

        return IpRecordDataImp(ip)


class IpRecordDataImp(IpRecordData):
    @property
    def ip_address(self) -> Union[IPv6Address, IPv4Address, None]:
        return self.__ip_address

    def __init__(self, ip: Union[IPv6Address, IPv4Address, None] = None):
        self.__ip_address = ip


class MxRecordData(ParseableRecordData, ABC):
    @property
    @abstractmethod
    def priority(self) -> Union[int, None]:
        pass

    @property
    @abstractmethod
    def target(self) -> Union[str, None]:
        pass

    @property
    def raw(self) -> str:
        priority = self.normalize_priority(self.priority)
        target = self.normalize_target(self.target)

        return f"{priority} {target}"

    @staticmethod
    def parse(data: Union[str, None]) -> MxRecordData:
        if data is None:
            return MxRecordDataImp()

        match = re.match("^(?P<priority>[0-9]+)\\s+(?P<target>[^\\s]+)$", data.strip())

        if not match:
            raise ValueError(f"Invalid MX record data: {data}")

        priority = int(match.group("priority"))
        target = match.group("target")

        return MxRecordDataImp(priority, target)

    @staticmethod
    def normalize_priority(priority: Union[int, None]) -> int:
        return priority or 0

    @staticmethod
    def normalize_target(target: Union[str, None]) -> str:
        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class MxRecordDataImp(MxRecordData):
    @property
    def priority(self) -> Union[int, None]:
        return self.__priority

    @property
    def target(self) -> Union[str, None]:
        return self.__target

    def __init__(self, priority: Union[int, None] = None, target: Union[str, None] = None):
        self.__priority = self.normalize_priority(priority)
        self.__target = self.normalize_target(target)


class SrvRecordData(ParseableRecordData, ABC):
    @property
    @abstractmethod
    def priority(self) -> Union[int, None]:
        pass

    @property
    @abstractmethod
    def weight(self) -> Union[int, None]:
        pass

    @property
    @abstractmethod
    def port(self) -> Union[int, None]:
        pass

    @property
    @abstractmethod
    def target(self) -> Union[str, None]:
        pass

    @property
    def raw(self) -> str:
        priority = self.normalize_priority(self.priority)
        weight = self.normalize_weight(self.weight)
        port = self.normalize_port(self.port)
        target = self.normalize_target(self.target)

        return f"{priority} {weight} {port} {target}"

    @staticmethod
    def parse(data: Union[str, None]) -> SrvRecordData:
        if data is None:
            return SrvRecordDataImp()

        match = re.match("^(?P<priority>[0-9]+)\\s+(?P<weight>[0-9]+)\\s+(?P<port>[0-9]+)\\s+(?P<target>[^\\s]+)$", data.strip())

        if not match:
            raise ValueError(f"Invalid SRV record data: {data}")

        priority = int(match.group("priority"))
        weight = int(match.group("weight"))
        port = int(match.group("port"))
        target = match.group("target")

        return SrvRecordDataImp(priority, weight, port, target)

    @staticmethod
    def normalize_priority(priority: Union[int, None]) -> int:
        return priority or 0

    @staticmethod
    def normalize_weight(weight: Union[int, None]) -> int:
        return weight or 0

    @staticmethod
    def normalize_port(port: Union[int, None]) -> int:
        return port or 0

    @staticmethod
    def normalize_target(target: Union[str, None]) -> str:
        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class SrvRecordDataImp(SrvRecordData):
    @property
    def priority(self) -> Union[int, None]:
        return self.__priority

    @property
    def weight(self) -> Union[int, None]:
        return self.__weight

    @property
    def port(self) -> Union[int, None]:
        return self.__port

    @property
    def target(self) -> Union[str, None]:
        return self.__target

    def __init__(self, priority: Union[int, None] = None, weight: Union[int, None] = None, port: Union[int, None] = None, target: Union[str, None] = None):
        self.__priority = self.normalize_priority(priority)
        self.__weight = self.normalize_weight(weight)
        self.__port = self.normalize_port(port)
        self.__target = self.normalize_target(target)


class CnameRecordData(ParseableRecordData, ABC):
    @property
    @abstractmethod
    def target(self) -> Union[str, None]:
        pass

    @property
    def raw(self) -> str:
        return self.normalize_target(self.target)

    @staticmethod
    def parse(data: Union[str, None]) -> CnameRecordData:
        if data is None:
            return CnameRecordDataImp()

        data = data.strip()
        match = re.match("\\s", data)

        if match:
            raise ValueError("CNAME data field should not contain whitespace")

        return CnameRecordDataImp(data)

    @staticmethod
    def normalize_target(target: Union[str, None]) -> str:
        target = target or "."

        if not target.endswith("."):
            target += "."

        return target


class CnameRecordDataImp(CnameRecordData):
    @property
    def target(self) -> Union[str, None]:
        return self.__target

    def __init__(self, target: Union[str, None] = None):
        self.__target = self.normalize_target(target)


class TxtRecordData(ParseableRecordData, ABC):
    @property
    @abstractmethod
    def normalized(self) -> str:
        pass

    @classmethod
    def parse(cls, data: Union[str, None]) -> TxtRecordData:
        if data is None:
            return TxtRecordDataImp()

        normalized_data = cls.unqoute_data(data)
        raw_data = cls.quote_data(normalized_data)

        return TxtRecordDataImp(raw_data, normalized_data)

    @staticmethod
    def unqoute_data(data: Union[str, None] = None) -> str:
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
    def quote_data(data: Union[str, None] = None) -> str:
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


class TxtRecordDataImp(TxtRecordData):
    @property
    def normalized(self) -> str:
        return self.__normalized

    @property
    def raw(self) -> str:
        return self.__raw

    def __init__(self, raw_data: Union[str, None] = None, normalized_data: Union[str, None] = None):
        self.__raw = raw_data
        self.__normalized = normalized_data
