#!/usr/bin/env python3

from __future__ import annotations

import json
import requests

from copy import deepcopy
from enum import Enum, auto
from typing import Any, Dict, Optional


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
    def __init__(self, method: HttpMethod, url: str, params: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None, data: Any = None):
        self.method = method
        self.url: str = url
        self.params: Dict[str, str] = params or {}
        self.headers: Dict[str, str] = headers or {}
        self.data: Any = data


class Http:
    @property
    def base_url(self) -> Optional[str]:
        return None

    @property
    def authorization(self) -> Optional[str]:
        return None

    def check_response(self, request: HttpRequest, response: requests.Response) -> Optional[Dict[str, Any]]:
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                return None

        raise Exception(response.text)

    def mangle_request(self, request: HttpRequest) -> HttpRequest:
        if self.authorization:
            request.headers.setdefault("Authorization", self.authorization)

        if request.method.is_post_like() and request.data and not isinstance(request.data, bytes) and not isinstance(request.data, str):
            request.data = json.dumps(request.data)
            request.headers.setdefault("Content-Type", "application/json")

        return request

    def mangle_paged_request(self, request: HttpRequest, page: int) -> HttpRequest:
        request.params["page"] = str(page)

        return request

    def mangle_response(self, request: HttpRequest, response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        data = self.select_data(request, response)
        pages = self.select_pages(request, response)

        if pages is None or pages <= 1 or not isinstance(data, list):
            return data if data is not None else response

        for page in range(2, pages + 1):
            page_request = self.mangle_paged_request(deepcopy(request), page)
            page_response = self.__send_internal(page_request)
            page_data = self.select_data(request, page_response)

            if page_data and isinstance(page_data, list):
                data += page_data

        return data

    def select_data(self, request: HttpRequest, response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return None

    def select_pages(self, request: HttpRequest, response: Optional[Dict[str, Any]]) -> Optional[int]:
        return None

    def __send_internal(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        kwargs = {}

        if request.method.is_post_like():
            kwargs["data"] = request.data

        if request.method.is_get_like():
            kwargs["allow_redirects"] = True

        url = f"{self.base_url.rstrip('/')}/{request.url.lstrip('/')}" if self.base_url else request.url
        response = requests.request(request.method.requests_name, url, params=request.params, headers=request.headers, **kwargs)

        return self.check_response(request, response)

    def __send(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        request = self.mangle_request(request)
        data = self.__send_internal(request)

        return self.mangle_response(request, data)

    def delete(self, url, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.DELETE, url, params=params, headers=headers, data=data))

    def get(self, url, params=None, headers=None):
        return self.__send(HttpRequest(HttpMethod.GET, url, params=params, headers=headers))

    def patch(self, url, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.PATCH, url, params=params, headers=headers, data=data))

    def post(self, url, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.POST, url, params=params, headers=headers, data=data))

    def put(self, url, params=None, headers=None, data=None):
        return self.__send(HttpRequest(HttpMethod.PUT, url, params=params, headers=headers, data=data))


class HttpStatic:
    @staticmethod
    def make_static(instance: Http):
        class StaticHttp:
            api = instance

            @classmethod
            def delete(cls, url, params=None, headers=None):
                return cls.api.delete(url, params=params, headers=headers)

            @classmethod
            def get(cls, url, params=None, headers=None):
                return cls.api.get(url, params=params, headers=headers)

            @classmethod
            def patch(cls, url, params=None, headers=None, data=None):
                return cls.api.patch(url, params=params, headers=headers, data=data)

            @classmethod
            def post(cls, url, params=None, headers=None, data=None):
                return cls.api.post(url, params=params, headers=headers, data=data)

            @classmethod
            def put(cls, url, params=None, headers=None, data=None):
                return cls.api.put(url, params=params, headers=headers, data=data)

        return StaticHttp
