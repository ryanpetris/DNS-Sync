#!/usr/bin/env python3

from .args import get_arguments
from ..commandbase import Command


def start():
    commands = Command.get_all()
    arguments = get_arguments()
    command = next(c for c in commands if c.id == arguments.command)

    command.run(arguments)
