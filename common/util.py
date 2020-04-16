#!/usr/bin/env python3

import inspect

from typing import Any, ClassVar
from types import FunctionType


class paramvalidate:
    def __init__(self, position, expected_type, message):
        self.__class__.__validate_position(position)
        self.__class__.__validate_type(expected_type)
        self.__class__.__validate_message(message)

        self.positions = position if isinstance(position, list) else [position]
        self.types = expected_type if isinstance(expected_type, list) else [expected_type]
        self.message = message

    def __call__(self, func):
        self.func = func

        return self.__run

    def __run(self, *args, **kwargs):
        for item in self.positions:
            if isinstance(item, int):
                if len(args) > item:
                    self.__validate_value(args[item])

            elif isinstance(item, str):
                if item in kwargs:
                    self.__validate_value(kwargs[item])

        return self.func(*args, **kwargs)

    def __validate_value(self, value):
        for check_type in self.types:
            if isinstance(value, check_type):
                return

            if inspect.isclass(value) and issubclass(value, check_type):
                return

        raise ValueError(self.message)

    @staticmethod
    def __validate_position(position):
        if isinstance(position, int):
            return

        if isinstance(position, str):
            return

        if isinstance(position, list):
            for item in position:
                if isinstance(item, int):
                    continue

                if isinstance(item, str):
                    continue

                raise ValueError("position must be an int, string, or a list of ints and strings")

            return

        raise ValueError("position must be an int, string, or a list of ints and strings")

    @staticmethod
    def __validate_type(expected_type):
        if inspect.isclass(expected_type):
            return

        if isinstance(expected_type, list):
            for item in expected_type:
                if inspect.isclass(item):
                    continue

                raise ValueError("type must be a class or a list of classes")

            return

        raise ValueError("type must be a class or a list of classes")

    @staticmethod
    def __validate_message(message):
        if isinstance(message, str):
            return

        raise ValueError("message must be a string")


@paramvalidate(0, [FunctionType, type], "func must be a function or class")
@paramvalidate([2, "extype"], BaseException, "extype must be a subclass of BaseException")
class tryit:
    def __init__(self, func: FunctionType, default: Any = None, extype: ClassVar = ValueError):
        self.func = func
        self.default_value = default
        self.expected_exception_type = extype

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except self.expected_exception_type:
            return self.default_value


