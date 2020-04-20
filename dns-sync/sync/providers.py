#!/usr/bin/env python3

import importlib
import os

from ..zonebase import Provider
from typing import Dict


def get_providers() -> Dict[str, Provider]:
    providers_module = importlib.import_module("..providers", package=__package__)
    providers_path = providers_module.__path__[0]
    providers: Dict[str, Provider] = {}

    for module_name in os.listdir(providers_path):
        module_path = os.path.join(providers_path, module_name)

        if not os.path.isdir(module_path):
            continue

        try:
            module = importlib.import_module(f"..providers.{module_name}", package=__package__)
            provider = module.Provider()
            providers[module_name] = provider
        except:
            pass

    return providers
