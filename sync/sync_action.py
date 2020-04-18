#!/usr/bin/env python3

from zonebase import Record


class SyncAction:
    def submit(self):
        pass


class CreateSyncAction(SyncAction):
    def __init__(self, source: Record):
        self.source: Record = source

    def __str__(self):
        return f"Create {self.source.host} {self.source.ttl} IN {self.source.type} {self.source.data}"


class UpdateSyncAction(SyncAction):
    def __init__(self, source: Record, destination: Record):
        self.source: Record = source
        self.destination: Record = destination

    def __str__(self):
        parts = []

        parts.append("Update")
        parts.append(f"{self.source.host}")

        if self.source.ttl != self.destination.ttl:
            parts.append(f"({self.destination.ttl or 0} -> {self.source.ttl or 0})")
        else:
            parts.append(f"{self.destination.ttl or 0}")

        parts.append("IN")
        parts.append(f"{self.destination.type}")
        parts.append(f"{self.destination.data}")

        if self.destination.data != self.source.data:
            parts.append("->")
            parts.append(f"{self.source.data}")

        return " ".join(parts)


class DeleteSyncAction(SyncAction):
    def __init__(self, destination: Record):
        self.destination: Record = destination

    def __str__(self):
        return f"Delete {self.destination.host} {self.destination.ttl} IN {self.destination.type} {self.destination.data}"
