# -*- coding: utf-8 -*-

import json
from http.client import HTTPConnection, HTTPSConnection
from typing import Final
from urllib.parse import urlparse

CONNECT_PATH_TEMPLATE: Final[str] = "/api/agents/{slug}/connect"


def request_ticket(uri: str, slug: str, token: str) -> str:
    parsed = urlparse(uri)
    path = CONNECT_PATH_TEMPLATE.format(slug=slug)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    conn: HTTPConnection
    if parsed.scheme == "https":
        conn = HTTPSConnection(parsed.netloc)
    else:
        conn = HTTPConnection(parsed.netloc)

    try:
        conn.request("POST", path, body="", headers=headers)
        resp = conn.getresponse()
        if resp.status != 200:
            body = resp.read().decode(errors="replace")
            raise RuntimeError(f"Ticket request failed ({resp.status}): {body}")
        data = json.loads(resp.read())
        return data["url"]
    finally:
        conn.close()
