#!/usr/bin/env python3

import os
import requests

from ...httpbase import Http, HttpStatic, HttpRequest
from base64 import b64encode
from typing import Any, Dict, Union


class Api(Http):
    @property
    def base_url(self) -> Union[str, None]:
        return self.__base_url

    @property
    def authorization(self) -> Union[str, None]:
        return f"Basic {self.__token}"

    def __init__(self, username: str = None, password: str = None):
        self.__base_url = os.environ.get("NAMECOM_API_URL", "https://api.name.com/v4/").rstrip("/")

        username = username or os.environ.get("NAMECOM_API_USERNAME")
        password = password or os.environ.get("NAMECOM_API_PASSWORD")

        self.__token = b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

        if not self.__token:
            raise ValueError("token must be specified or NAMECOM_API_TOKEN environment variable must exist.")

    def check_response(self, request: HttpRequest, response: requests.Response) -> Union[Dict[str, Any], None]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if 200 <= response.status_code < 300:
            return response_json

        if response_json and "errors" in response_json and response_json["errors"]:
            raise Exception(f"{response_json['message']}: {response_json['details']}" if "details" in response_json else response_json["message"])

        raise Exception(response.text)

    def select_data(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        if not response:
            return None

        if "records" in response:
            return response["records"]

        if "domains" in response:
            return response["domains"]

        return None

    def select_pages(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[int, None]:
        return response and "lastPage" in response and response["lastPage"] or None


StaticApi = HttpStatic.make_static(Api())
