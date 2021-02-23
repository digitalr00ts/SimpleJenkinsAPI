import logging
import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Tuple, Union

from SimpleJenkinsAPI import __metadata__
import httpx


USER_AGENT = f"{__metadata__.name}/{__metadata__.version} (+{__metadata__.homepage})"


def response_headers(response):
    logging.debug(response.headers)


def response_time(response):
    logging.debug("Response elapsed %ss.", timedelta.total_seconds(response.elapsed))


def raise_on_error(response):
    response.raise_for_status()


@dataclass
class SimpleJenkins:
    jenkins_url: Union[httpx.URL, str] = os.environ.get("JENKINS_URL")
    auth: Union[httpx.Auth, Tuple[str, str]] = None
    headers: httpx.Headers = field(default=httpx.Headers({"User-Agent": USER_AGENT}), repr=False)
    _client: httpx.Client = field(default=None, init=False, repr=False, hash=False)

    def __post_init__(self):
        if self.jenkins_url is None:
            raise TypeError("required positional argument: 'jenkins_url'")
        if self.auth is None:
            self.auth = (os.environ.get("JENKINS_USER_ID"), os.environ.get("JENKINS_API_TOKEN"))
        if isinstance(self.auth, tuple):
            self.auth = httpx.BasicAuth(*self.auth)

    def __enter__(self):
        self.open_client()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __bool__(self):
        try:
            response = self.get_response()
        except httpx.RequestError as err:
            logging.error(err)
            return False
        return True if response.status_code == 200 else False

    def _url_strip(self, url: str):
        return url.strip("/") if isinstance(url, str) else url

    def get_response(self, url: Union[httpx.URL, str] = "/", method: str = "GET", **kwargs):
        url = self._url_strip(url)
        if any(i_ in kwargs for i_ in ["data", "json", "content", "files"]):
            method = "POST"
        request = self._client.build_request(method, url, **kwargs)
        return self._client.send(request)

    def open_client(self):
        event_hooks = {
            "response": [response_headers, response_time, raise_on_error],
        }
        self._client = httpx.Client(
            auth=self.auth,
            headers=self.headers,
            base_url=self.jenkins_url,
            http2=True,
            event_hooks=event_hooks,
        )

    def client(self):
        return self._client

    def close(self):
        self._client.close()


@dataclass
class SimpleJenkinsAPIs(SimpleJenkins):
    def __post_init__(self):
        self.headers.update({"Accept": "application/json"})

    def api(self, url: Union[httpx.URL, str] = "", tree: str = "", depth: int = 0, **kwargs):
        url = f"{self._url_strip(url)}/api/json"
        kwargs["params"] = kwargs.get("params", {})
        kwargs["params"]["depth"] = depth
        if tree:
            kwargs["params"]["tree"] = tree

        return self.get_response(url=url, **kwargs).json()

    def blue(self, url, **kwargs):
        url = f"blue/rest/{self._url_strip(url)}"
        if "data" in kwargs:
            logging.warning("Use `json` rather than `data` for Blue Ocean API.  ")
            kwargs["json"] = kwargs.popitem("data")
        return self.get_response(url, **kwargs).json()

    def casc(self, url, **kwargs):
        """
        [https://docs.cloudbees.com/docs/cloudbees-ci-api/latest/bundle-management-api
        """
        url = f"casc-bundle/{self._url_strip(url)}"
        return self.get_response(url, **kwargs).json()
