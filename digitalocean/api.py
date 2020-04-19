#!/usr/bin/env python3

import os
import requests
import urllib.parse

from httpbase import Http, HttpStatic, HttpRequest
from typing import Any, Dict, Union


class Api(Http):
    @property
    def base_url(self) -> Union[str, None]:
        return self.__base_url

    @property
    def authorization(self) -> Union[str, None]:
        return f"Bearer {self.__token}"

    def __init__(self, token: str = None):
        self.__base_url = os.environ.get("DO_API_URL", "https://api.digitalocean.com/v2/").rstrip("/")
        self.__token = token or os.environ.get("DO_API_TOKEN")

        if not self.__token:
            raise ValueError("token must be specified or DO_API_TOKEN environment variable must exist.")

    def mangle_request(self, request: HttpRequest) -> HttpRequest:
        request = super().mangle_request(request)

        # use maxiumum page size that's allowed per documentation
        request.params["per_page"] = str(200)

        return request

    def check_response(self, request: HttpRequest, response: requests.Response) -> Union[Dict[str, Any], None]:
        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if 200 <= response.status_code < 300:
            return response_json

        if "message" in response_json:
            raise Exception(f"{response_json['id']}: {response_json['message']}" if "id" in response_json else response_json["message"])

        raise Exception(response.text)

    def select_data(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        if not response:
            return None

        if "domains" in response:
            return response["domains"]

        if "domain_records" in response:
            return response["domain_records"]

        if "domain_record" in response:
            return response["domain_record"]

        return None

    def select_pages(self, request: HttpRequest, response: Union[Dict[str, Any], None]) -> Union[int, None]:
        if not response or "links" not in response or "pages" not in response["links"] or "last" not in response["links"]["pages"]:
            return None

        url = urllib.parse.urlparse(response["links"]["pages"]["last"])
        url_query = urllib.parse.parse_qs(url.query)

        if "page" not in url_query or not url_query["page"]:
            return None

        return int(next(iter(url_query["page"])))


StaticApi = HttpStatic.make_static(Api())
