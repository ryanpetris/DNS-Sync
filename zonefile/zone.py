#!/usr/bin/env python3

import os

from .record import Record, RecordDefaults
from queue import PriorityQueue


class Zone:
    export_tab_width = 8

    def __init__(self, data=None):
        self.defaults = None
        self.records = []

        record_lines = []
        default_lines = []

        for line in data.split("\n"):
            line = line.replace("\r", "").strip()

            if not line:
                continue

            if line.startswith("$"):
                default_lines.append(line)
            else:
                record_lines.append(line)

        self.defaults = RecordDefaults(default_lines)

        for line in record_lines:
            self.records.append(Record(line, self.defaults))

    def __str__(self):
        outlines = []
        cls = self.__class__

        if self.defaults:
            outlines.append(f"{self.defaults}")

        longest_host = 0
        longest_ttl = 0

        for record in self.records:
            longest_host = max(longest_host, len(record.host))

            if record.has_ttl:
                longest_ttl = max(longest_ttl, len(f"{record.ttl.seconds}"))

        longest_host_columns = longest_host // cls.export_tab_width + 1
        longest_ttl_columns = longest_ttl // cls.export_tab_width + 1

        for record in self.records:
            host = record.host + "\t" * (longest_host_columns - (len(record.host) // cls.export_tab_width + 1) + 1)
            ttl = ""

            if longest_ttl:
                ttl = f"{record.ttl.seconds}" if record.has_ttl else ""
                ttl += "\t" * (longest_ttl_columns - (len(ttl) // cls.export_tab_width + 1) + 1)

            outlines.append(f"{host}{ttl}IN\t{record.type}\t{record.data}")

        return "\n".join(outlines)

    @staticmethod
    def read_zone(file):
        if not os.path.exists(file):
            raise FileNotFoundError(f"File {file} does not exist.")

        queue = PriorityQueue()
        zonedata = []
        priority = 0
        basepath = os.path.dirname(file)

        with open(file, "r") as f:
            for line in f.readlines():
                priority += 1
                queue.put((priority, line.strip()))

        while not queue.empty():
            priority, line = queue.get()

            if line.startswith("$INCLUDE"):
                _, include_file = line.split(" ")

                include_path = os.path.join(basepath, include_file)

                if not os.path.exists(include_path):
                    raise FileNotFoundError(f"Could not import file {include_path}")

                with open(include_path, "r") as f:
                    for line in reversed(f.readlines()):
                        priority -= 1
                        queue.put((priority, line.strip()))

                continue

            zonedata.append(line)

        return Zone("\n".join(zonedata))

