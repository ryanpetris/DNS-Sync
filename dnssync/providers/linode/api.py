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
        return f"Bearer {self.__token}"

    def __init__(self, token: str = None):
        self.__base_url = os.environ.get("LINODE_API_URL", "https://api.linode.com/v4/")
        self.__token = token or os.environ.get("LINODE_API_TOKEN")

        if not self.__token:
            raise ValueError("token must be specified or LINODE_API_TOKEN environment variable must exist.")

    def check_response(self, request: HttpRequest, response: requests.Response) -> Optional[Dict[str, Any]]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if 200 <= response.status_code < 300:
            return response_json

        if response_json and "errors" in response_json and response_json["errors"]:
            raise Exception("\n".join(f"{x['field']}: {x['reason']}" if "field" in x else f"{x['reason']}" for x in response_json["errors"]))

        raise Exception(response.text)

    def select_data(self, request: HttpRequest, response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return response and "data" in response and response["data"] or None

    def select_pages(self, request: HttpRequest, response: Optional[Dict[str, Any]]) -> Optional[int]:
        return response and "pages" in response and response["pages"] or None


StaticApi = HttpStatic.make_static(Api())
