#!/usr/bin/env python3

from ...zonebase import Provider


def list_providers():
    providers = Provider.get_all()

    for provider in sorted(providers, key=lambda p: p.id):
        print(f"{provider.id}: {provider.description}")
