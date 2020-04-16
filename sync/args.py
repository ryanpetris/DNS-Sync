#!/usr/bin/env python3

import sys

from argparse import ArgumentParser


def get_arguments(providers):
    provider_options = [key for key, value in providers.items()]
    parser = ArgumentParser()

    parser.add_argument(
        "-z",
        "--zone-path",
        dest="zonepath",
        help="path to zonefiles",
        required=True
    )

    parser.add_argument(
        "-p",
        "--provider",
        dest="provider",
        choices=provider_options,
        help="remote dns provider",
        required=len(provider_options) > 1
    )

    return parser.parse_args(sys.argv[1:])
