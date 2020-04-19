#!/usr/bin/env python3

from .sync_action import SyncAction, UpdateSyncAction, CreateSyncAction, DeleteSyncAction
from ..common import DnsRecordType
from ..zonebase import Provider, Record
from typing import Dict, List, Tuple


def sync_zone(zone: str, source_provider: Provider, destination_provider: Provider):
    source_zone = source_provider.get_zone(zone)
    destination_zone = destination_provider.get_zone(zone)

    if not source_zone:
        print(f"Zone {zone} does not exist in source provider {source_provider.id}")
        return

    if not destination_zone:
        print(f"Zone {zone} does not exist in destination provider {destination_provider.id}")
        return

    print(f"Syncing zone {zone} from {source_provider.id} to {destination_provider.id}")

    source_types: Dict[Tuple[str, DnsRecordType], List[Record]] = {}
    destination_types: Dict[Tuple[str, DnsRecordType], List[Record]] = {}
    sync_actions: List[SyncAction] = []

    for record in source_zone.records:
        # Skip records from the source that the destination cannot write.
        if not destination_provider.can_write_type(record.type):
            continue

        key = (record.host, record.type)

        if key not in source_types:
            source_types[key] = []

        source_types[key].append(record)

    for record in destination_zone.records:
        # Skip records from the destination that the source cannot read.
        if not source_provider.can_read_type(record.type):
            continue

        # If the destination provider can read a type but not write it, then don't sync it.
        if not destination_provider.can_write_type(record.type):
            continue

        key = (record.host, record.type)

        if key not in destination_types:
            destination_types[key] = []

        destination_types[key].append(record)

    all_types: List[Tuple[str, DnsRecordType]] = [*set([*source_types.keys()] + [*destination_types.keys()])]

    for record_type in all_types:
        source_records = source_types[record_type] if record_type in source_types else []
        destination_records = destination_types[record_type] if record_type in destination_types else []

        for source_record in [r for r in source_records]:
            destination_record = next((r for r in destination_records if r.data.normalized == source_record.data.normalized), None)

            if destination_record:
                if source_record.ttl != destination_record.ttl:
                    sync_actions.append(UpdateSyncAction(source_record, destination_record))

                source_records.remove(source_record)
                destination_records.remove(destination_record)

    for record_type in all_types:
        source_records = source_types[record_type] if record_type in source_types else []
        destination_records = destination_types[record_type] if record_type in destination_types else []

        for source_record in source_records:
            destination_record = next(iter(destination_records), None)

            if destination_record:
                sync_actions.append(UpdateSyncAction(source_record, destination_record))
                destination_records.remove(destination_record)
                continue

            sync_actions.append(CreateSyncAction(source_record))

        for destination_record in destination_records:
            sync_actions.append(DeleteSyncAction(destination_record))

    for action in sync_actions:
        print(action)

        if isinstance(action, CreateSyncAction):
            destination_provider.create_record(zone, action.source)
            continue

        if isinstance(action, UpdateSyncAction):
            destination_provider.update_record(zone, action.destination, action.source)
            continue

        if isinstance(action, DeleteSyncAction):
            destination_provider.delete_record(zone, action.destination)
