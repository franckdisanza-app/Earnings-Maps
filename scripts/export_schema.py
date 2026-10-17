"""Write schemas/earnings.schema.json from the pydantic model."""

import json
import sys

from common import ROOT
from earnings_model import Earnings

SCHEMA_PATH = ROOT / "schemas" / "earnings.schema.json"


def schema_text() -> str:
    schema = Earnings.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://earningsmaps.com/schemas/earnings.schema.json"
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    SCHEMA_PATH.write_text(schema_text(), encoding="utf-8", newline="\n")
    print(f"wrote {SCHEMA_PATH.relative_to(ROOT)}", file=sys.stderr)
