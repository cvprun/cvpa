# -*- coding: utf-8 -*-

from typing import Tuple

from cvpa.variables import AGENT_TOKEN_PREFIX


def parse_agent_token(combined: str, prefix=AGENT_TOKEN_PREFIX) -> Tuple[str, str]:
    if not combined.startswith(prefix):
        raise ValueError(f"Agent token must start with the '{prefix}' prefix")

    prefix_len = len(prefix)
    rest = combined[prefix_len:]
    sep_idx = rest.find("_")
    if sep_idx == -1:
        raise ValueError(f"Agent token must be in the form '{prefix}{{hex}}_{{slug}}'")

    hex_part = rest[:sep_idx]
    slug = rest[sep_idx + 1 :]
    if not hex_part or not slug:
        raise ValueError("Agent token must contain non-empty hex and slug parts")

    token = f"{prefix}{hex_part}"
    return slug, token
