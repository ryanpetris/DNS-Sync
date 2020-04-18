#!/usr/bin/env python3

from .record import Record
from abc import ABC, abstractmethod
from typing import List, Union


class Zone(ABC):
    @property
    @abstractmethod
    def domain(self) -> Union[str, None]:
        pass

    @property
    @abstractmethod
    def records(self) -> List[Record]:
        pass

    def __str__(self) -> str:
        export_tab_width = 8
        outlines = []
        longest_host = 0
        longest_ttl = 0

        for record in self.records:
            longest_host = max(longest_host, len(record.host))

            if record.serialize_ttl:
                longest_ttl = max(longest_ttl, len(f"{record.ttl.seconds}"))

        longest_host_columns = longest_host // export_tab_width + 1
        longest_ttl_columns = longest_ttl // export_tab_width + 1

        for record in self.records:
            host = record.host + "\t" * (longest_host_columns - (len(record.host) // export_tab_width + 1) + 1)
            ttl = ""

            if longest_ttl:
                ttl = f"{record.ttl.seconds}" if record.serialize_ttl else ""
                ttl += "\t" * (longest_ttl_columns - (len(ttl) // export_tab_width + 1) + 1)

            outlines.append(f"{host}{ttl}IN\t{record.type}\t{record.data}")

        return "\n".join(outlines)

    @staticmethod
    def normalize_domain(domain: Union[str, None]) -> Union[str, None]:
        if domain is None:
            return None

        domain = domain.strip().rstrip(".")

        if not domain:
            return None

        return domain
