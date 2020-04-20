#!/usr/bin/env python3

import os
import requests

from ...httpbase import Http, HttpStatic, HttpRequest
from typing import Any, Dict, Optional


class Api(Http):
    @property
    def base_url(self) -> Optional[str]:
        return self.__base_url

    @property
    def authorization(self) -> Optional[str]:
        return f"sso-key {self.__api_key}:{self.__api_secret}"

    def __init__(self, api_key: str = None, api_secret: str = None, shopper_id: str = None):
        self.__base_url = os.environ.get("GD_API_URL", "https://api.godaddy.com/v1/")
        self.__api_key = api_key or os.environ.get("GD_API_KEY")
        self.__api_secret = api_secret or os.environ.get("GD_API_SECRET")
        self.__shopper_id = shopper_id or os.environ.get("GD_SHOPPER_ID")

        if not self.__api_key or not self.__api_secret:
            raise ValueError("api_key and api_secret must be specified or GD_API_KEY and GD_API_SECRET environment variables must exist.")

    def mangle_request(self, request: HttpRequest) -> HttpRequest:
        request = super().mangle_request(request)

        if self.__shopper_id:
            request.headers.setdefault("X-Shopper-Id", self.__shopper_id)

        return request

    def check_response(self, request: HttpRequest, response: requests.Response) -> Optional[Dict[str, Any]]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if 200 <= response.status_code < 300:
            return response_json

        if "message" in response_json:
            raise Exception(f"{response_json['code']}: {response_json['message']}")

        raise Exception(response.text)


StaticApi = HttpStatic.make_static(Api())
