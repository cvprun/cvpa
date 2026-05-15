# -*- coding: utf-8 -*-

from typing import Final


class ErrorCode:
    MISSING_AUTH: Final[str] = "missing_auth"
    INVALID_TOKEN: Final[str] = "invalid_token"
    TOKEN_VERSION_MISMATCH: Final[str] = "token_version_mismatch"
    AGENT_NOT_FOUND: Final[str] = "agent_not_found"
    AGENT_SUSPENDED: Final[str] = "agent_suspended"
    AGENT_TERMINATING: Final[str] = "agent_terminating"
    AGENT_REMOVED: Final[str] = "agent_removed"
    MISSING_TICKET: Final[str] = "missing_ticket"
    INVALID_TICKET: Final[str] = "invalid_ticket"
    RATE_LIMITED: Final[str] = "rate_limited"
    INTERNAL: Final[str] = "internal"
    VALIDATION_ERROR: Final[str] = "validation_error"
    HANDLER_ERROR: Final[str] = "handler_error"
