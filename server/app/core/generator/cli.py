"""Read-only CLI for previewing a registered CRUD generation plan."""

import argparse
import json
from pathlib import Path

from .executor import execute_crud_generation
from .plan import build_registered_crud_generation_plan
from .validator import validate_generated_output


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview a registered CRUD generation plan")
    parser.add_argument("resource", help="registered resource name, for example users")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="generation root directory")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true", help="create missing scaffold files")
    modes.add_argument("--check", action="store_true", help="validate existing generated files")
    args = parser.parse_args()

    try:
        plan = build_registered_crud_generation_plan(args.resource)
    except KeyError:
        parser.error(f"unknown registered resource: {args.resource}")
    output = (
        validate_generated_output(plan, args.root)
        if args.check
        else execute_crud_generation(plan, args.root, dry_run=False)
        if args.write
        else plan
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output.get("valid", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
