#!/usr/bin/env python3

import sys

from argparse import ArgumentParser
from typing import Dict
from zonebase import Provider


def get_arguments(providers: Dict[str, Provider]):
    source_providers = [k for k, p in providers.items()]
    destination_providers = [k for k, p in providers.items() if not p.read_only]
    parser = ArgumentParser()

    parser.add_argument(
        "-s",
        "--source",
        dest="source",
        choices=source_providers,
        help="source dns provider",
        required=len(source_providers) > 1
    )

    parser.add_argument(
        "-d",
        "--destination",
        dest="destination",
        choices=destination_providers,
        help="destination dns provider",
        required=len(destination_providers) > 1
    )

    parser.add_argument(
        "-z",
        "--zone",
        dest="zones",
        action="append",
        help="zones to sync, or all if none specified"
    )

    return parser.parse_args(sys.argv[1:])
