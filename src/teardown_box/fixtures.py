from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Fixtures:
    root: Path

    def read_text(self, rel: str) -> Optional[str]:
        p = self.root / rel
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8")

    def read_json(self, rel: str) -> Optional[Dict]:
        txt = self.read_text(rel)
        if txt is None:
            return None
        return json.loads(txt)

    def read_csv_dicts(self, rel: str) -> Optional[List[Dict[str, str]]]:
        p = self.root / rel
        if not p.exists():
            return None
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def exists(self, rel: str) -> bool:
        return (self.root / rel).exists()
