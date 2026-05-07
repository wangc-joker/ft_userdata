import json
from pathlib import Path
from typing import Any


class StateStore:
    """Tiny JSON state store for runtime memory that should survive reloads."""

    def __init__(self, namespace: str) -> None:
        self.namespace = namespace
        self.path = Path("user_data") / "strategy_state" / f"{namespace}.json"
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")

    def set_pair_state(self, pair: str, key: str, value: Any) -> None:
        self.data.setdefault(pair, {})[key] = value
        self._save()

    def get_pair_state(self, pair: str, key: str, default: Any = None) -> Any:
        return self.data.get(pair, {}).get(key, default)

