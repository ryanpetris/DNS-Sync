#!/usr/bin/env python3

from . import get_arguments, get_providers, sync


def main():
    providers = get_providers()
    arguments = get_arguments(providers)

    zonepath = arguments.zonepath

    if arguments.provider:
        provider = providers[arguments.provider]
    else:
        provider = next(value for key, value in providers.items())

    zones = provider.get_all()

    sync(zones, zonepath)


if __name__ == "__main__":
    main()
