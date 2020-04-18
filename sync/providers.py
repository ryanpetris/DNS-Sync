#!/usr/bin/env python3


def get_provider(namespace):
    try:
        module = __import__(namespace)
        return module.Provider()
    except Exception as e:
        return None


def get_providers():
    providers = [
        get_provider("zonefile"),
        get_provider("linode"),
        get_provider("cloudflare")
    ]

    return {p.id: p for p in providers if p is not None}
