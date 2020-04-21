#!/usr/bin/env python3

from .args import get_arguments
from ..commandbase import Command


def start():
    arguments = get_arguments()
    command = next(c for c in Command.get_all() if c.id == arguments.command)

    command.run(arguments)
