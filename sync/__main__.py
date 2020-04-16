#!/usr/bin/env python3

import os

from .sync_action import SyncAction, UpdateSyncAction, CreateSyncAction, DeleteSyncAction
from cfsync.zone import Zone as CfZone
from typing import List
from zonefile import Zone as DnsZone, RecordType as DnsRecordType

zones = CfZone.get_all()

for cf_zone in zones:
    zonefile_path = os.path.join("..", "powerdns", "zones", f"{cf_zone.domain.lower()}.db")

    if not os.path.exists(zonefile_path):
        print(f"Skipping zone {cf_zone.domain} (no zonefile)")
        continue

    print(f"Syncing zone {cf_zone.domain}")

    dns_zone = DnsZone.read_zone(zonefile_path)
    cf_zone.fetch_records()

    all_types = []
    cf_types = {}
    dns_types = {}
    sync_actions: List[SyncAction] = []

    for record in cf_zone.records:
        if record.type is None:
            continue

        key = (record.host, record.type)

        if key not in cf_types:
            cf_types[key] = []

        if key not in all_types:
            all_types.append(key)

        cf_types[key].append(record)

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
        cf_records = cf_types[record_type] if record_type in cf_types else []
        dns_records = dns_types[record_type] if record_type in dns_types else []

        for dns_record in [r for r in dns_records]:
            normalized_data = dns_record.data.get_normalized_data()
            cf_record = next((r for r in cf_records if r.data == normalized_data), None)

            if cf_record:
                cf_records.remove(cf_record)
                dns_records.remove(dns_record)

    for record_type in all_types:
        cf_records = cf_types[record_type] if record_type in cf_types else []
        dns_records = dns_types[record_type] if record_type in dns_types else []

        for dns_record in dns_records:
            cf_record = next(iter(cf_records), None)

            if cf_record:
                cf_records.remove(cf_record)
                sync_actions.append(UpdateSyncAction(cf_record, dns_record))
                continue

            sync_actions.append(CreateSyncAction(cf_zone, dns_record))

        for cf_record in cf_records:
            sync_actions.append(DeleteSyncAction(cf_record))

    for action in sync_actions:
        print(action)
        action.submit()





