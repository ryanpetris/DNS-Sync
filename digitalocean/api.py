#!/usr/bin/env python3

import os
import requests
import urllib.parse

from httpbase import Http, HttpStatic, HttpRequest
from typing import Any, Dict, Union


def dataonly(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if "domains" in response:
            return response["domains"]

        if "domain_records" in response:
            return response["domain_records"]

        if "domain_record" in response:
            return response["domain_record"]

        return  response

    return wrapper


def autopage(func):
    def clean_response(response):
        del response["links"]

        if "meta" in response:
            if "domains" in response:
                response["meta"]["total"] = len(response["domains"])

            if "domain_records" in response:
                response["meta"]["total"] = len(response["domain_records"])

        return response

    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if "params" in kwargs and kwargs["params"] and "page" in kwargs["params"]:
            return response

        if "links" not in response or "pages" not in response["links"]:
            return response

        url = urllib.parse.urlparse(response["links"]["pages"]["last"])
        url_query = urllib.parse.parse_qs(url.query)
        pages = int(next(iter(url_query["page"])))

        if pages <= 1:
            return clean_response(response)

        for page in range(2, pages + 1):
            new_kwargs = {**kwargs}
            new_kwargs["params"] = {**new_kwargs["params"]} if "params" in new_kwargs and new_kwargs["params"] else {}
            new_kwargs["params"]["page"] = page

            page_response = func(*args, **new_kwargs)

            if "domains" in response:
                response["domains"] += page_response["domains"]

            if "domain_records" in response:
                response["domain_records"] += page_response["domain_records"]

        return clean_response(response)

    return wrapper


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

        self.get = dataonly(autopage(self.get))
        self.post = dataonly(self.post)
        self.put = dataonly(self.put)

    def mangle_request(self, request: HttpRequest) -> HttpRequest:
        request = super().mangle_request(request)

        # use maxiumum page size that's allowed per documentation
        request.params["per_page"] = 200

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


StaticApi = HttpStatic.make_static(Api())
