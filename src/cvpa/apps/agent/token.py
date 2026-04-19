# -*- coding: utf-8 -*-

from typing import Tuple

from cvpa.variables import AGENT_TOKEN_PREFIX


def parse_agent_token(combined: str) -> Tuple[str, str]:
    if not combined.startswith(AGENT_TOKEN_PREFIX):
        raise ValueError(
            f"Agent token must start with the '{AGENT_TOKEN_PREFIX}' prefix"
        )

    rest = combined[len(AGENT_TOKEN_PREFIX) :]
    sep_idx = rest.find("_")
    if sep_idx == -1:
        raise ValueError(
            "Agent token must be in the form "
            f"'{AGENT_TOKEN_PREFIX}{{slug}}_{{token}}'"
        )

    slug = rest[:sep_idx]
    token = rest[sep_idx + 1 :]
    if not slug or not token:
        raise ValueError("Agent token must contain non-empty slug and token parts")

    return slug, token
