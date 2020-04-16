#!/usr/bin/env python3


class SyncAction:
    def submit(self):
        pass


class UpdateSyncAction(SyncAction):
    def __init__(self, old_record, new_record):
        self.old_record = old_record
        self.new_record = new_record

    def __str__(self):
        return f"Update {self.old_record.host} IN {self.old_record.type} {self.old_record.data} -> {self.new_record.data.get_normalized_data()}"

    def submit(self):
        self.old_record.update(self.new_record)


class CreateSyncAction(SyncAction):
    def __init__(self, zone, new_record):
        self.zone = zone
        self.new_record = new_record

    def __str__(self):
        return f"Create {self.new_record}"

    def submit(self):
        self.zone.create_record(self.new_record)


class DeleteSyncAction(SyncAction):
    def __init__(self, old_record):
        self.old_record = old_record

    def __str__(self):
        return f"Delete {self.old_record}"

    def submit(self):
        self.old_record.delete()
