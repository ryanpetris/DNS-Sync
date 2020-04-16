#!/usr/bin/env python3

import os

from .sync_action import SyncAction, UpdateSyncAction, CreateSyncAction, DeleteSyncAction
from typing import List
from zonefile import Zone as DnsZone, RecordType as DnsRecordType


def sync_zone(host_zone, zonefile_path):
    zonefile_path = os.path.join(zonefile_path, f"{host_zone.domain.lower()}.db")

    if not os.path.exists(zonefile_path):
        print(f"Skipping zone {host_zone.domain} (no zonefile)")
        return

    print(f"Syncing zone {host_zone.domain}")

    dns_zone = DnsZone.read_zone(zonefile_path)
    host_zone.fetch_records()

    all_types = []
    host_types = {}
    dns_types = {}
    sync_actions: List[SyncAction] = []

    for record in host_zone.records:
        if record.type is None:
            continue

        key = (record.host, record.type)

        if key not in host_types:
            host_types[key] = []

        if key not in all_types:
            all_types.append(key)

        host_types[key].append(record)

    for record in dns_zone.records:
        if record.type in [DnsRecordType.SOA, DnsRecordType.NS]:
            continue

        key = (record.host, record.type)

        if key not in dns_types:
            dns_types[key] = []

        if key not in all_types:
            all_types.append(key)

        dns_types[key].append(record)

    for record_type in all_types:
        host_records = host_types[record_type] if record_type in host_types else []
        dns_records = dns_types[record_type] if record_type in dns_types else []

        for dns_record in [r for r in dns_records]:
            normalized_data = dns_record.data.get_normalized_data()
            host_record = next((r for r in host_records if r.get_normalized_data() == normalized_data), None)

            if host_record:
                host_records.remove(host_record)
                dns_records.remove(dns_record)

    for record_type in all_types:
        host_records = host_types[record_type] if record_type in host_types else []
        dns_records = dns_types[record_type] if record_type in dns_types else []

        for dns_record in dns_records:
            host_record = next(iter(host_records), None)

            if host_record:
                host_records.remove(host_record)
                sync_actions.append(UpdateSyncAction(host_record, dns_record))
                continue

            sync_actions.append(CreateSyncAction(host_zone, dns_record))

        for host_record in host_records:
            sync_actions.append(DeleteSyncAction(host_record))

    for action in sync_actions:
        print(action)
        action.submit()


def sync(host_zones, zonefile_path):
    for host_zone in host_zones:
        sync_zone(host_zone, zonefile_path)
