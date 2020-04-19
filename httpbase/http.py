#!/usr/bin/env python3

from __future__ import annotations

import json
import requests

from enum import Enum, auto
from typing import Any, Dict, Union


class HttpMethod(Enum):
    GET = auto()
    HEAD = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    PATCH = auto()

    @property
    def requests_name(self):
        return self.name.lower()

    def is_get_like(self):
        return self in [
            HttpMethod.GET,
            HttpMethod.HEAD,
            HttpMethod.CONNECT,
            HttpMethod.OPTIONS,
            HttpMethod.TRACE
        ]

    def is_post_like(self):
        return self in [
            HttpMethod.POST,
            HttpMethod.PUT,
            HttpMethod.DELETE,
            HttpMethod.PATCH
        ]


class HttpRequest:
    def __init__(self, method: HttpMethod, url: str, params: Union[Dict[str, str], None] = None, headers: Union[Dict[str, str], None] = None, data: Any = None):
        self.method = method
        self.url: str = url
        self.params: Dict[str, str] = params or {}
        self.headers: Dict[str, str] = headers or {}
        self.data: Any = data


class Http:
    @property
    def base_url(self) -> Union[str, None]:
        return None

    @property
    def authorization(self) -> Union[str, None]:
        return None

    def check_response(self, request: HttpRequest, response: requests.Response) -> Union[Dict[str, Any], None]:
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                return None

        raise Exception(response.text)

    def mangle_request(self, request: HttpRequest) -> HttpRequest:
        if self.authorization and "Authorization" not in request.headers:
            request.headers["Authorization"] = self.authorization

        if request.method.is_post_like() and request.data and isinstance(request.data, dict):
            request.data = json.dumps(request.data)

            if "Content-Type" not in request.headers:
                request.headers["Content-Type"] = "application/json"

        return request

    def mangle_response(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        return response

    def __send(self, request: HttpRequest) -> Union[Dict[str, Any], None]:
        request = self.mangle_request(request)
        kwargs = {}

        if request.method.is_post_like():
            kwargs["data"] = request.data

        if request.method.is_get_like():
            kwargs["allow_redirects"] = True

        url = f"{self.base_url.rstrip('/')}/{request.url.lstrip('/')}" if self.base_url else request.url
        response = requests.request(request.method.requests_name, url, params=request.params, headers=request.headers, **kwargs)
        data = self.check_response(request, response)

        return self.mangle_response(request, data)

    def delete(self, url, *, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.DELETE, url, params=params, headers=headers, data=data))

    def get(self, url, *, params=None, headers=None):
        return self.__send(HttpRequest(HttpMethod.GET, url, params=params, headers=headers))

    def patch(self, url, *, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.PATCH, url, params=params, headers=headers, data=data))

    def post(self, url, *, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.POST, url, params=params, headers=headers, data=data))

    def put(self, url, *, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.PUT, url, params=params, headers=headers, data=data))


class HttpStatic:
    @staticmethod
    def make_static(instance: Http):
        class StaticHttp:
            api = instance

            @classmethod
            def delete(cls, url, *, params=None, headers=None):
                return cls.api.delete(url, params=params, headers=headers)

            @classmethod
            def get(cls, url, *, params=None, headers=None):
                return cls.api.get(url, params=params, headers=headers)

            @classmethod
            def patch(cls, url, *, params=None, headers=None, data=None):
                return cls.api.patch(url, params=params, headers=headers, data=data)

            @classmethod
            def post(cls, url, *, params=None, headers=None, data=None):
                return cls.api.post(url, params=params, headers=headers, data=data)

            @classmethod
            def put(cls, url, *, params=None, headers=None, data=None):
                return cls.api.put(url, params=params, headers=headers, data=data)

        return StaticHttp
