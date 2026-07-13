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
dashboard = read("src/dashboard.lava")
all_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix in TEXT_SUFFIXES
)

assert manifest["recipe_id"] == "oneall:event-registration-analytics-dashboard"
assert manifest["concept_ids"] == [
    "event-registration",
    "lava",
    "data-views-reports",
    "security-permissions",
]

id_keys = [key for key in config if key.endswith("Id")]
assert id_keys and all(config[key] == 0 for key in id_keys)
assert config["capacityFallback"] == 0
assert 1 <= config["maxRegistrantRows"] <= 1000

assert "registrationInstanceId <= 0" in dashboard
assert "@RegistrationInstanceId" in dashboard
assert "rr.OnWaitList = 0" in dashboard
assert "COUNT(DISTINCT CASE WHEN OnWaitList = 0 THEN RegistrationId END)" in dashboard
assert "DATEADD(day, -@DaysRemaining, @PriorEnd)" in dashboard
assert "WHEN IsStaff = 1 THEN 'staff'" in dashboard
assert "WHEN IsServingVerified = 1 THEN 'nonstaff-serving'" in dashboard
assert "RegistrationRegistrantFee" in dashboard
assert "MaximumUsageCount" in dashboard
assert "OptionLabelSuffixMarker" in dashboard
assert "COUNT(*) OVER () AS TotalRegistrantRows" in dashboard
assert "BETWEEN 1 AND 1000" in dashboard
assert "overflow-y:hidden" in dashboard
assert "| Escape" in dashboard

assert dashboard.count("{% sql") == dashboard.count("{% endsql %}")
for opening, closing in (("if", "endif"), ("for", "endfor"), ("case", "endcase")):
    assert len(re.findall(r"{%\s*" + opening + r"\b", dashboard)) == len(
        re.findall(r"{%\s*" + closing + r"\b", dashboard)
    )
assert not re.search(
    r"(?i)\b(update|insert|delete|merge|execute|exec|drop|alter|truncate)\b",
    dashboard,
)
assert not re.search(
    r"(?i)oneandall\.church|admin\.oneandall|/Users/|LeadCon|All Staff|Serve Badge|Campus Coordinators",
    all_text,
)
assert not re.search(r"(?i)\b(email|phone|mobilephone|street1|postalcode)\b", dashboard)

print("event-registration-analytics-dashboard static contract: ok")
