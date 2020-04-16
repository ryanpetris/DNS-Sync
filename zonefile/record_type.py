#!/usr/bin/env python3

from enum import Enum


class RecordType(Enum):
    A = 1
    AAAA = 28
    CNAME = 5
    MX = 15
    NS = 2
    PTR = 12
    SOA = 6
    SPF = 99
    SRV = 33
    TXT = 16

    @staticmethod
    def parse(record_type):
        try:
            return RecordType[record_type.upper()]
        except KeyError:
            raise ValueError(f"{record_type} is not a valid record type")

    def __str__(self):
        return self.name
