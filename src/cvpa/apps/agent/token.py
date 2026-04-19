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
            "Agent token must be in the form " f"'{AGENT_TOKEN_PREFIX}{{hex}}_{{slug}}'"
        )

    hex_part = rest[:sep_idx]
    slug = rest[sep_idx + 1 :]
    if not hex_part or not slug:
        raise ValueError("Agent token must contain non-empty hex and slug parts")

    token = f"{AGENT_TOKEN_PREFIX}{hex_part}"
    return slug, token
