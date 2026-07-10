#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".lava", ".md", ".sql"}


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


manifest = json.loads(read("recipe.json"))
mapping = json.loads(read("config/mapping.example.json"))
deploy = read("src/workflowtype-deploy.lava")
verify_sql = read("tests/verify-transfer.sql")
all_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix in TEXT_SUFFIXES
)

assert manifest["recipe_id"] == "oneall:registration-to-connection-request"
assert mapping["workflow"]["connectionOpportunityGuid"] == ""
assert mapping["workflow"]["connectionStatusGuid"] == ""
assert mapping["duplicatePolicy"] == "stop_and_review"

for required in (
    "RegistrationRegistrantId",
    "ConnectionOpportunity",
    "ConnectionStatus",
    "ConnectionRequest",
    "SourceRegistrationId",
    "MappedValue",
):
    assert required in deploy

assert "registrationregistrant.Registration.Campus.Guid" in deploy
assert "registrationregistrant.RegistrationId" in deploy
assert "ConnectionRequestAttribute" in deploy
assert "CampusAttribute" in deploy
assert "ForeignKey" in deploy
assert "canonical" in deploy.lower()
assert "RegistrantWorkflowTypeId" not in deploy
assert "admin." not in deploy.lower()

sql_without_comments = re.sub(r"/\*.*?\*/", "", verify_sql, flags=re.S)
sql_without_comments = re.sub(r"--.*?$", "", sql_without_comments, flags=re.M)
assert re.search(r"\bSELECT\b", sql_without_comments, flags=re.I)
assert not re.search(
    r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|TRUNCATE|EXEC(?:UTE)?)\b",
    sql_without_comments,
    flags=re.I,
)

assert not re.search(r"(?i)oneandall\.church|admin\.oneandall|/Users/", all_text)
assert not re.search(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
    all_text,
)
assert not re.search(r"\b(?:RegistrationTemplate|RegistrationInstance|ConnectionOpportunity|WorkflowType)Id\s*[:=]\s*[1-9][0-9]+\b", all_text)

print("registration-to-connection-request static contract: ok")
