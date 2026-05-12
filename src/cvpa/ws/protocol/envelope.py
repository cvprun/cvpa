# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Envelope:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    ts: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"type": self.type}
        if self.id is not None:
            out["id"] = self.id
        if self.ts is not None:
            out["ts"] = self.ts
        if self.data:
            out["data"] = self.data
        return out

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Envelope":
        return cls(
            type=raw["type"],
            data=raw.get("data") or {},
            id=raw.get("id"),
            ts=raw.get("ts"),
        )
