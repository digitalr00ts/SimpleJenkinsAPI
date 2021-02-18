import logging
import os
import urllib.error
import urllib.parse
from base64 import b64encode
from dataclasses import dataclass, field
from typing import Optional, Tuple, Union
from urllib import request

from SimpleJenkinsAPI import __metadata__


@dataclass
class Credentials:
    user: Optional[str] = os.environ.get("JENKINS_USER_ID")
    password: Optional[str] = field(default=os.environ.get("JENKINS_API_TOKEN"), repr=False)

    @property
    def token(self) -> Optional[str]:
        if bool(self):
            return b64encode(f"{self.user}:{self.password}".encode()).decode()

        logging.info("Jenkins credentials not found.")

    def __bool__(self) -> bool:
        return all([self.user, self.password])


@dataclass
class JenkinsAPI:
    url: Optional[str] = os.environ.get("JENKINS_URL")
    auth: Optional[Union[Credentials, Tuple[str, str]]] = field(default=Credentials(), repr=False)
    api: str = "json"
    _request: request.Request = field(
        default=request.Request(
            "https://",
            headers={
                "User-Agent": f"{__metadata__.name}/{__metadata__.version} (+{__metadata__.homepage})",
            },
        ),
        init=False,
        repr=False,
    )

    def __post_init__(self):
        if not self.url:
            raise RuntimeError("url parameter required.")
        self._set_auth()
        self._request.add_header("Accept", f"application/{self.api}")
        self.url = self.url.rstrip("/")

    def _set_auth(self):
        if isinstance(self.auth, tuple):
            self.auth = Credentials(*self.auth)
        if not bool(self.auth):
            self._request.remove_header("Authorizaton")
        else:
            self._request.add_header("Authorization", f"Basic {self.auth.token}")

    def get(self, endpoint: str = "", tree: str = "", depth=0, pretty=False):
        params = {"depth": depth}
        if tree:
            params["tree"] = tree
        if pretty:
            params["pretty"] = pretty
        self._request.full_url = "/".join(
            [self.url, endpoint, "api", self.api, f"?{urllib.parse.urlencode(params)}"],
        )
        logging.debug("Endpoint set to %s", self._request.full_url)

        try:
            with request.urlopen(self._request, timeout=5) as response:
                if response.getcode() != 200:
                    raise urllib.error.HTTPError(
                        response.url,
                        response.status,
                        response.msg,
                        response.headers,
                        response.fileno(),
                    )
                rtn = response.read().decode()
        except urllib.error.HTTPError as err:
            logging.error(err)

        return rtn

    def __bool__(self) -> bool:
        try:
            self.get(tree="_class")
        except urllib.error.HTTPError:
            return False

        return True
