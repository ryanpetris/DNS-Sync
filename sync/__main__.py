#!/usr/bin/env python3

from . import get_arguments, get_providers, sync_zone


def main():
    providers = get_providers()
    arguments = get_arguments(providers)

    if arguments.source:
        source_provider = providers[arguments.source]
    else:
        source_provider = next(value for key, value in providers.items())

    if arguments.destination:
        destination_provider = providers[arguments.destination]
    else:
        destination_provider = next(value for key, value in providers.items())

    if arguments.zones:
        zones = arguments.zones
    else:
        zones = destination_provider.list_zones()

    for zone in sorted(zones):
        sync_zone(zone, source_provider, destination_provider)


if __name__ == "__main__":
    main()
