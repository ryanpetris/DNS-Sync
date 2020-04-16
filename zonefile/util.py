#!/usr/bin/env python3

import re

from common import paramvalidate
from typing import Any


@paramvalidate([0, "seconds"], [int, str], "time must be an int or string")
class Time:
    time_regex = re.compile("^((?P<weeks>[0-9]+)[wW])?((?P<days>[0-9]+)[dD])?((?P<hours>[0-9]+)[hH])?((?P<minutes>[0-9]+)[mM])?((?P<seconds>[0-9]+)[sS])?$")
    number_regex = re.compile("^[0-9]+$")

    minute_seconds = 60
    hour_seconds = minute_seconds * 60
    day_seconds = hour_seconds * 24
    week_seconds = day_seconds * 7

    def __init__(self, time: Any = None):
        self.seconds = 0
        self.__was_formatted = False

        if not time:
            return

        if isinstance(time, int):
            self.seconds = time
            return

        if self.__class__.number_regex.match(time):
            self.seconds = int(time)
            return

        match = self.__class__.time_regex.match(time)

        if not match:
            raise ValueError(f"Invalid time value: {time}")

        self.seconds = \
            int(match.group("seconds") or 0) + \
            int(match.group("minutes") or 0) * self.__class__.minute_seconds + \
            int(match.group("hours") or 0) * self.__class__.hour_seconds + \
            int(match.group("days") or 0) * self.__class__.day_seconds + \
            int(match.group("weeks") or 0) * self.__class__.week_seconds

        self.__was_formatted = True

    def __str__(self):
        if not self.__was_formatted:
            return f"{self.seconds}"

        parts = []
        seconds = self.seconds

        weeks = seconds // self.__class__.week_seconds

        if weeks:
            seconds %= self.__class__.week_seconds
            parts.append(f"{weeks}w")

        days = seconds // self.__class__.day_seconds

        if days:
            seconds %= self.__class__.day_seconds
            parts.append(f"{days}d")

        hours = seconds // self.__class__.hour_seconds

        if hours:
            seconds %= self.__class__.hour_seconds
            parts.append(f"{hours}h")

        minutes = seconds // self.__class__.minute_seconds

        if minutes:
            seconds %= self.__class__.minute_seconds
            parts.append(f"{minutes}m")

        if seconds:
            parts.append(f"{seconds}s")

        return "".join(parts)


