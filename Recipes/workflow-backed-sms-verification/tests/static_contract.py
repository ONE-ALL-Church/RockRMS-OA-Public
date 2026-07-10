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
start = read("src/verify-start.lava")
check = read("src/verify-check.lava")
final = read("src/final-submit-recheck.lava")
all_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix in TEXT_SUFFIXES
)

assert manifest["recipe_id"] == "oneall:workflow-backed-sms-verification"
assert config["verificationWorkflowTypeGuid"] == ""
assert config["mobilePhoneTypeValueId"] == 0
assert "WHERE c.TotalMatches = 1" in start
assert "CRYPT_GEN_RANDOM" in start
assert "CodeHash" in start and "Attempts" in check and "ExpiresAt" in check
assert "ConsumedAt" in final and "UPDLOCK, HOLDLOCK" in final
assert "PersonAlias" not in check
assert "name=\"verificationSession\"" in start
assert "name=\"verifiedAlias" not in all_text
assert "name=\"personId" not in all_text
assert "name=\"aliasId" not in all_text
assert not re.search(r"(?i)oneandall\.church|admin\.oneandall|/Users/", all_text)
assert not re.search(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
    all_text,
)

print("workflow-backed-sms-verification static contract: ok")
