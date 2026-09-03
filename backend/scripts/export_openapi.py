"""Dump the OpenAPI document so the frontend client can be generated from it."""

import json
import sys
from pathlib import Path

from app.main import create_app


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    destination.write_text(json.dumps(create_app().openapi(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
