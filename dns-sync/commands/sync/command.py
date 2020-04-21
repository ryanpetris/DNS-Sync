#!/usr/bin/env python3

from ...commandbase import Command as BaseCommand
from ...zonebase import Provider
from .sync_zone import sync_zone
from argparse import Namespace, ArgumentParser
from typing import List


class Command(BaseCommand):
    def __init__(self):
        self.providers: List[Provider] = Provider.get_all()

    def populate_argument_parser(self, parser: ArgumentParser):
        parser.description = "Sync DNS records between providers."

        source_providers = sorted(p.id for p in self.providers)
        destination_providers = sorted(p.id for p in self.providers if not p.read_only)

        parser.add_argument(
            metavar="source",
            dest="source",
            choices=source_providers,
            help="source dns provider"
        )

        parser.add_argument(
            metavar="destination",
            dest="destination",
            choices=destination_providers,
            help="destination dns provider"
        )

        parser.add_argument(
            "-z",
            "--zone",
            metavar="zone",
            dest="zones",
            action="append",
            help="zones to sync, or all if none specified"
        )

    def run(self, arguments: Namespace):
        source_provider = next(p for p in self.providers if p.id == arguments.source)
        destination_provider = next(p for p in self.providers if p.id == arguments.destination)

        if arguments.zones:
            zones = arguments.zones
        else:
            zones = destination_provider.list_zones()

        for zone in sorted(zones):
            sync_zone(zone, source_provider, destination_provider)
