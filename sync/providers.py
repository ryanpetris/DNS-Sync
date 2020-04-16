#!/usr/bin/env python3


def get_providers():
    providers = {}

    try:
        from cfsync import Zone

        providers["cloudflare"] = Zone
    except:
        pass

    try:
        from linode import Zone

        providers["linode"] = Zone
    except:
        pass

    return providers
