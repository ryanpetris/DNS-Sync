#!/usr/bin/env python3

import json
import os
import requests


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


class Api:
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("CF_API_TOKEN")
        self.base_url = os.environ.get("CF_API_URL", "https://api.cloudflare.com/client/v4/").rstrip("/")

        if not self.token:
            raise ValueError("token must be specified or CF_API_TOKEN environment variable must exist.")

    def __get_default_headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    def __get_url(self, url):
        return f"{self.base_url}/{url.lstrip('/')}"

    @staticmethod
    def __check_response(response):
        if 200 <= response.status_code < 300:
            return

        response_json = None

        try:
            response_json = response.json()
        except:
            pass

        if response_json and "errors" in response_json and response_json["errors"]:
            raise Exception("\n".join(f"{x['code']}: {x['message']}" for x in response_json["errors"]))

        raise Exception(response.text)

    @dataonly
    @autopage
    def get(self, url, params=None, headers=None):
        headers = {**self.__get_default_headers(), **(headers or {})}

        response = requests.get(self.__get_url(url), params=params, headers=headers)

        self.__check_response(response)

        return response.json()

    @dataonly
    def post(self, url, params=None, headers=None, data=None):
        headers = {**self.__get_default_headers(), **(headers or {})}

        if data and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        if data:
            data = json.dumps(data)

        response = requests.post(self.__get_url(url), params=params, headers=headers, data=data)

        self.__check_response(response)

        return response.json()

    @dataonly
    def put(self, url, params=None, headers=None, data=None):
        headers = {**self.__get_default_headers(), **(headers or {})}

        if data and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        if data:
            data = json.dumps(data)

        response = requests.put(self.__get_url(url), params=params, headers=headers, data=data)

        self.__check_response(response)

        return response.json()

    def delete(self, url, params=None, headers=None):
        headers = {**self.__get_default_headers(), **(headers or {})}

        response = requests.delete(self.__get_url(url), params=params, headers=headers)

        self.__check_response(response)

        return response.json()


class StaticApi:
    api = Api()

    @classmethod
    def get(cls, url, params=None, headers=None):
        return cls.api.get(url, params=params, headers=headers)

    @classmethod
    def post(cls, url, params=None, headers=None, data=None):
        return cls.api.post(url, params=params, headers=headers, data=data)

    @classmethod
    def put(cls, url, params=None, headers=None, data=None):
        return cls.api.put(url, params=params, headers=headers, data=data)

    @classmethod
    def delete(cls, url, params=None, headers=None):
        return cls.api.delete(url, params=params, headers=headers)
