#!/usr/bin/env python3

import os
import requests

from ...httpbase import Http, HttpStatic, HttpRequest
from typing import Any, Dict, Union


class Api(Http):
    @property
    def base_url(self) -> Union[str, None]:
        return self.__base_url

    @property
    def authorization(self) -> Union[str, None]:
        return f"Bearer {self.__token}"

    def __init__(self, token: str = None):
        self.__base_url = os.environ.get("CF_API_URL", "https://api.cloudflare.com/client/v4/")
        self.__token = token or os.environ.get("CF_API_TOKEN")

        if not self.__token:
            raise ValueError("token must be specified or CF_API_TOKEN environment variable must exist.")

    def check_response(self, request: HttpRequest, response: requests.Response) -> Union[Dict[str, Any], None]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if 200 <= response.status_code < 300:
            return response_json

        if response_json and "errors" in response_json and response_json["errors"]:
            raise Exception("\n".join(f"{x['code']}: {x['message']}" for x in response_json["errors"]))

        raise Exception(response.text)

    def select_data(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        return response and "result" in response and response["result"] or None

    def select_pages(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[int, None]:
        return response and "result_info" in response and "total_pages" in response["result_info"] and response["result_info"]["total_pages"] or None


StaticApi = HttpStatic.make_static(Api())
