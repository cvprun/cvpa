# -*- coding: utf-8 -*-

import json
from http.client import HTTPConnection, HTTPSConnection
from logging import Logger
from time import monotonic
from typing import Final, Optional
from urllib.parse import urlparse

from cvpa.logging.loggers import agent_logger
from cvpa.ws.protocol import ErrorCode

CONNECT_PATH_TEMPLATE: Final[str] = "/api/agents/{slug}/connect"
LOG_BODY_MAX_CHARS: Final[int] = 512


class TicketError(Exception):
    def __init__(self, status: int, code: Optional[str], message: str) -> None:
        self.status = status
        self.code = code
        self.message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        if self.code:
            return f"Ticket request failed ({self.status}, {self.code}): {self.message}"
        return f"Ticket request failed ({self.status}): {self.message}"

    @property
    def is_auth_failure(self) -> bool:
        return self.status == 401

    @property
    def is_suspended(self) -> bool:
        return self.status == 403 and self.code == ErrorCode.AGENT_SUSPENDED

    @property
    def is_terminating(self) -> bool:
        return self.status == 403 and self.code == ErrorCode.AGENT_TERMINATING

    @property
    def is_not_found(self) -> bool:
        return self.status == 404

    @property
    def is_retryable(self) -> bool:
        return self.status == 429 or self.status >= 500


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def _truncate(text: str, limit: int = LOG_BODY_MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def _parse_error(raw: bytes, content_type: str) -> tuple[Optional[str], str]:
    body_text = raw.decode(errors="replace")
    if "application/json" in content_type:
        try:
            data = json.loads(body_text)
        except json.JSONDecodeError:
            return None, _truncate(body_text)
        if isinstance(data, dict):
            code = data.get("code")
            message = data.get("message") or body_text
            return (
                code if isinstance(code, str) else None,
                _truncate(message if isinstance(message, str) else body_text),
            )
    return None, _truncate(body_text)


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
            code, message = _parse_error(raw, content_type)
            log.debug(
                f"Ticket response body: {_truncate(raw.decode(errors='replace'))}"
            )
            raise TicketError(status=resp.status, code=code, message=message)

        data = json.loads(raw)
        ws_url = data["url"]
        log.debug(f"Ticket issued: {ws_url}")
        return ws_url
    finally:
        conn.close()
