"""Local, source-labelled lookup for selected central-government schemes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "government_schemes.json"


def lookup_government_scheme(scheme_query: str) -> dict[str, Any]:
    """Find a scheme by its name or common alias without claiming live eligibility."""
    query = (scheme_query or "").strip().casefold()
    if not query:
        return {"found": False, "error": "Please provide a scheme name or common abbreviation."}
    try:
        dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"found": False, "error": "The local scheme information is temporarily unavailable."}

    for scheme in dataset["schemes"]:
        names = [scheme["name"], *scheme.get("aliases", [])]
        if any(query in name.casefold() or name.casefold() in query for name in names):
            return {"found": True, "data_type": dataset["data_type"], "as_of": dataset["as_of"], "source_note": dataset["source_note"], "scheme": scheme}
    return {"found": False, "data_type": dataset["data_type"], "as_of": dataset["as_of"], "error": "This scheme is not in ArthMitra's local central-government scheme dataset."}
