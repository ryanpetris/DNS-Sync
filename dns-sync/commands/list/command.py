#!/usr/bin/env python3

from .providers import list_providers
from ...commandbase import Command as BaseCommand
from argparse import Namespace, ArgumentParser


class Command(BaseCommand):
    def __init__(self):
        self.things = {
            "providers": list_providers
        }

    def populate_argument_parser(self, parser: ArgumentParser):
        parser.description = "List things."

        parser.add_argument(
            dest="thing",
            choices=sorted(self.things.keys()),
            help="thing to list"
        )

    def run(self, arguments: Namespace):
        self.things[arguments.thing]()
