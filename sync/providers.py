#!/usr/bin/env python3

from typing import Dict, Union
from zonebase import Provider


def get_provider(namespace: str) -> Union[Provider, None]:
    try:
        module = __import__(namespace)
        return module.Provider()
    except:
        return None


def get_providers() -> Dict[str, Provider]:
    providers = [
        get_provider("zonefile"),
        get_provider("linode"),
        get_provider("cloudflare")
    ]

    return {p.id: p for p in providers if p is not None}
