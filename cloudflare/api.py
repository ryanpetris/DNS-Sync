#!/usr/bin/env python3

import os
import requests

from httpbase import Http, HttpStatic, HttpRequest
from typing import Any, Dict, Union


def dataonly(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if "result" not in response:
            return response

        return response["result"]

    return wrapper


def autopage(func):
    def clean_response(response):
        del response["result_info"]["page"]
        del response["result_info"]["per_page"]
        del response["result_info"]["total_pages"]

        response["result_info"]["count"] = len(response["result"])
        response["result_info"]["total_count"] = len(response["result"])

        return response

    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        if "params" in kwargs and kwargs["params"] and "page" in kwargs["params"]:
            return response

        if "result_info" not in response or "total_pages" not in response["result_info"]:
            return response

        pages = response["result_info"]["total_pages"]

        if pages <= 1:
            return clean_response(response)

        for page in range(2, pages + 1):
            new_kwargs = {**kwargs}
            new_kwargs["params"] = {**new_kwargs["params"]} if "params" in new_kwargs and new_kwargs["params"] else {}
            new_kwargs["params"]["page"] = page

            page_response = func(*args, **new_kwargs)

            response["result"] += page_response["result"]

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
        self.__base_url = os.environ.get("CF_API_URL", "https://api.cloudflare.com/client/v4/").rstrip("/")
        self.__token = token or os.environ.get("CF_API_TOKEN")

        if not self.__token:
            raise ValueError("token must be specified or CF_API_TOKEN environment variable must exist.")

        self.get = dataonly(autopage(self.get))
        self.post = dataonly(self.post)
        self.put = dataonly(self.put)

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


StaticApi = HttpStatic.make_static(Api())
