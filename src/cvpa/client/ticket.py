# -*- coding: utf-8 -*-

import json
from http.client import HTTPConnection, HTTPSConnection
from logging import Logger
from time import monotonic
from typing import Final, Optional
from urllib.parse import urlparse

from cvpa.logging.loggers import agent_logger

CONNECT_PATH_TEMPLATE: Final[str] = "/api/agents/{slug}/connect"
LOG_BODY_MAX_CHARS: Final[int] = 512


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def _truncate(text: str, limit: int = LOG_BODY_MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def request_ticket(
    uri: str,
    slug: str,
    token: str,
    logger: Optional[Logger] = None,
) -> str:
    log = logger or agent_logger

    parsed = urlparse(uri)
    path = CONNECT_PATH_TEMPLATE.format(slug=slug)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    log.debug(
        f"Ticket request POST {parsed.scheme}://{parsed.netloc}{path} "
        f"slug={slug} token={_mask_token(token)}"
    )

    conn: HTTPConnection
    if parsed.scheme == "https":
        conn = HTTPSConnection(parsed.netloc)
    else:
        conn = HTTPConnection(parsed.netloc)

    started_at = monotonic()
    try:
        conn.request("POST", path, body="", headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        elapsed_ms = (monotonic() - started_at) * 1000.0
        content_type = resp.getheader("Content-Type", "")

        log.debug(
            f"Ticket response status={resp.status} "
            f"content_type={content_type!r} "
            f"bytes={len(raw)} elapsed={elapsed_ms:.1f}ms"
        )

        if resp.status != 200:
            body_text = raw.decode(errors="replace")
            log.debug(f"Ticket response body: {_truncate(body_text)}")
            raise RuntimeError(
                f"Ticket request failed ({resp.status}): {_truncate(body_text)}"
            )

        data = json.loads(raw)
        ws_url = data["url"]
        log.debug(f"Ticket issued: {ws_url}")
        return ws_url
    finally:
        conn.close()
