#!/usr/bin/env python3

import CloudFlare
import CloudFlare.exceptions

from .record import Record
from zonefile import Record as DnsRecord, RecordType as DnsRecordType


class Zone:
    def __init__(self, zoneinfo):
        self.cf_zone_id = zoneinfo["id"]
        self.domain = zoneinfo["name"]
        self.nameservers = zoneinfo["name_servers"]
        self.records = None

    def __str__(self):
        return self.domain

    def fetch_records(self):
        if self.records is not None:
            return

        cf = CloudFlare.CloudFlare(raw=True)

        page_number = 0
        records = []

        while True:
            page_number += 1

            try:
                raw_results = cf.zones.dns_records.get(self.cf_zone_id, params={'per_page': 100, 'page': page_number})
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                raise Exception('/zones.get - api call failed') from e

            records += [Record(self, z) for z in raw_results['result']]
            total_pages = raw_results['result_info']['total_pages']

            if page_number >= total_pages:
                break

        self.records = records

    def create_record(self, record: DnsRecord):
        cf = CloudFlare.CloudFlare()

        cf_record = {
            "name": record.host,
            "type": f"{record.type}",
            "content": record.data.get_normalized_data(),
            "proxied": False
        }

        if record.type == DnsRecordType.SRV:
            name_parts = record.host.split(".")

            cf_service, cf_proto = name_parts[:2]
            cf_name = ".".join(name_parts[2:]) or "@"

            cf_record = {
                "type": "SRV",
                "data": {
                    "service": cf_service,
                    "proto": cf_proto,
                    "name": cf_name,
                    "priority": record.data.priority,
                    "weight": record.data.weight,
                    "port": record.data.port,
                    "target": record.data.target
                },
                "proxied": False
            }

        try:
            new_record = cf.zones.dns_records.post(self.cf_zone_id, data=cf_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            raise Exception('/zones.dns_records.post %s %s - %s' % (self.domain, record.host, e))

        self.records.append(Record(self, new_record))

    @staticmethod
    def get_all():
        cf = CloudFlare.CloudFlare(raw=True)

        page_number = 0
        domains = []

        while True:
            page_number += 1

            try:
                raw_results = cf.zones.get(params={'per_page': 100, 'page': page_number})
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                raise Exception('/zones.get - api call failed') from e

            domains += [Zone(z) for z in raw_results['result']]
            total_pages = raw_results['result_info']['total_pages']

            if page_number >= total_pages:
                break

        return domains


