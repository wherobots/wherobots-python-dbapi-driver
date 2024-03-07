"""Wherobots DB driver.

A PEP-0249 compatible driver for interfacing with Wherobots DB.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection
import requests
import websockets

import errors


apilevel = "2.0"
threadsafety = 1
paramstyle = "pyformat"


DEFAULT_ENDPOINT = "api.wherobots.services"  # "api.cloud.wherobots.com"
STAGING_ENDPOINT = "api.staging.wherobots.services"  # "api.staging.wherobots.com"
DEFAULT_REGION = "aws-us-west-2"


def connect(
    host: str = DEFAULT_ENDPOINT,
    token: str = None,
    api_key: str = None,
    runtime: str = DEFAULT_RUNTIME,
    region: str = DEFAULT_REGION,
) -> DBAPIConnection:
    if not token and not api_key:
        raise ValueError("At least one of `token` or `api_key` is required")
    if token and api_key:
        raise ValueError("`token` and `api_key` can't be both provided")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif api_key:
        headers["X-API-Key"] = api_key

    resp = requests.post(
        url=f"https://{host}/sql/session",
        params={"runtime": runtime, "region": region},
        headers=headers,
    )
    resp.raise_for_status()

    ws_uri = resp.json().get("uri")
    if not ws_uri:
        raise errors.InterfaceError("Could not acquire SQL session")
    return WherobotsSession(ws=websockets.connect(ws_uri))


class WherobotsSession(DBAPIConnection):

    def __init__(self, ws):
        self.__ws = ws

    def close(self):
        pass

    def commit(self):
        raise errors.NotSupportedError

    def rollback(self):
        raise errors.NotSupportedError

    def cursor(self):
        raise errors.NotSupportedError
