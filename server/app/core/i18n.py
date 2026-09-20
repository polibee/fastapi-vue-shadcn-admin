import json
from functools import lru_cache
from pathlib import Path

from fastapi import Request

SUPPORTED_LOCALES = ("zh-CN", "en")


def locale_from_request(request: Request) -> str:
    header = request.headers.get("accept-language", "")
    return "zh-CN" if header.lower().startswith("zh") else "en"


@lru_cache
def _load(scope: str, locale: str) -> dict[str, str]:
    app_root = Path(__file__).parents[1]
    path = (app_root / "core" / "locales" / scope if scope == "errors" else app_root / scope / "locales") / f"{locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def translate(scope: str, key: str, locale: str) -> str:
    return _load(scope, locale).get(key, key)
