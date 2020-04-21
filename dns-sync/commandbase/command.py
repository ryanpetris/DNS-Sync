#!/usr/bin/env python3

from __future__ import annotations

import importlib
import os

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import List


class Command(ABC):
    @property
    def id(self) -> str:
        return self.__class__.__module__.split(".")[-2]

    @abstractmethod
    def populate_argument_parser(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def run(self, arguments: Namespace):
        pass

    @staticmethod
    def get_all() -> List[Command]:
        commands_module = importlib.import_module("..commands", package=__package__)
        commands_path = commands_module.__path__[0]
        commands: List[Command] = []

        for module_name in os.listdir(commands_path):
            module_path = os.path.join(commands_path, module_name)

            if not os.path.isdir(module_path):
                continue

            try:
                module = importlib.import_module(f"..commands.{module_name}", package=__package__)

                commands.append(module.Command())
            except:
                pass

        return commands
