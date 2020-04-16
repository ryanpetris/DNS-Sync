#!/usr/bin/env python3

from .api import StaticApi
from .record import Record


class Zone:
    def __init__(self, zoneinfo):
        self.id = zoneinfo["id"]
        self.domain = zoneinfo["domain"]
        self.soa_email = zoneinfo["soa_email"]
        self.records = []
        self.__records_fetched = False

    def fetch_records(self):
        if self.__records_fetched:
            return

        self.__records_fetched = True
        self.records = []

        for record in StaticApi.get(f"domains/{self.id}/records"):
            self.records.append(Record(record, self))

    def create_record(self, record):
        data = Record.get_request_info(record)

        if not data:
            return

        response = StaticApi.post(f"domains/{self.id}/records", data=data)

        self.records.append(Record(response, self))

    @staticmethod
    def get_all():
        for zone in StaticApi.get("domains"):
            yield Zone(zone)
