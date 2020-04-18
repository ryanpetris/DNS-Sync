#!/usr/bin/env python3

import re

from common import DnsRecordType, Time
from typing import Union
from zonebase import Record as BaseRecord, RecordData as BaseRecordData, TxtRecordData as BaseTxtRecordData


class Record(BaseRecord):
    @property
    def host(self) -> Union[str, None]:
        return self.__host

    @property
    def ttl(self) -> Union[Time, None]:
        return self.__ttl

    @property
    def type(self) -> Union[DnsRecordType, None]:
        return self.__type

    @property
    def data(self) -> Union[BaseRecordData, None]:
        return self.__data

    def __init__(self, record):
        self.id = record["id"]
        self.__host = BaseRecord.normalize_host(".".join(record["name"].split(".")[:-2]))
        self.__type = BaseRecord.normalize_type(record["type"])
        self.__ttl = None
        self.__data = None

        self.set_data(record)

    def set_data(self, record):
        ttl = record["ttl"]

        if ttl == 1:
            ttl = None

        self.__ttl = BaseRecord.normalize_ttl(ttl)

        content = record["content"]

        if self.type == DnsRecordType.SRV:
            content = re.sub("\\s+", " ", content)
            content = f"{record['priority']} {content}"

        if self.type in [DnsRecordType.TXT, DnsRecordType.SPF]:
            content = BaseTxtRecordData.quote_data(content)

        self.__data = BaseRecordData.type_parse(self.__type, content)
