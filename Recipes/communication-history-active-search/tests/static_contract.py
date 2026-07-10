#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".lava", ".md"}


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


manifest = json.loads(read("recipe.json"))
config = json.loads(read("config/configuration.example.json"))
results = read("src/results.lava")
all_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix in TEXT_SUFFIXES
)

assert manifest["recipe_id"] == "oneall:communication-history-active-search"
assert config["communicationDetailPageId"] == 0
assert "search:'{{ searchText }}'" in results
assert "@Search" in results
assert "SanitizeSql" not in results
assert "c.Message" not in results and "c.SMSMessage" not in results
assert "pageSize == 25 or pageSize == 50 or pageSize == 100" in results
assert "5000" not in results
assert "when 3 %}Approved" in results
assert "c.Status <> 0" in results
assert not re.search(r"(?i)oneandall\.church|admin\.oneandall|/Users/|/page/26[0-9]{2}", all_text)

print("communication-history-active-search static contract: ok")
