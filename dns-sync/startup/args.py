#!/usr/bin/env python3

import sys

from ..commandbase import Command
from argparse import ArgumentParser


def get_arguments():
    commands = Command.get_all()
    parser = ArgumentParser(allow_abbrev=False)

    subparsers = parser.add_subparsers(
        dest="command"
    )

    for command in commands:
        subparser = subparsers.add_parser(command.id)

        command.populate_argument_parser(subparser)

    return parser.parse_args(sys.argv[1:])
