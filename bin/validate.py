#!/usr/bin/env python3
"""Validate this repo's JSON Schemas and the fixtures they govern.

Run it with no arguments, from anywhere in the repo:

    python3 bin/validate.py

Exits 0 if every check passes, 1 if any fails. Warnings never fail the run.

Two things make validating this repo less obvious than it looks.

1.  Every cross-file reference is an absolute
    https://raw.githubusercontent.com/ifp/schemas/master/... URL, so a naive run
    resolves against `master` instead of your working tree — silently hiding the
    change you are testing. Every $ref is rewritten to the local tree here.

2.  Not every file under json/ is live. Abandoned work-in-progress sits alongside
    the published schemas, so the strict checks apply to the set reachable from the
    roots in PAIRS (following $refs transitively). Anything unreachable is reported
    as a warning: a file nothing references cannot break a consumer, but it should
    not be invisible either.

The repo went years with a public schema that was impossible to satisfy — its own
published example failed to validate — because nothing ever ran these checks.
"""

import json
import os
import sys

try:
    from jsonschema import Draft7Validator, RefResolver
except ImportError:
    sys.exit("jsonschema is not installed. Run: pip install 'jsonschema~=4.25'")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "https://raw.githubusercontent.com/ifp/schemas/master/"

# Fixture/example documents and the schema each one must satisfy.
# The schemas here are also the roots for the reachability walk.
PAIRS = [
    ("json/internal/internal_sale-advert-schema_v1.2.0.json", "json/fixtures/upsert_sale_advert.json"),
    ("json/internal/property/floor_plans-schema_v1.2.0.json", "json/fixtures/floor_plans.json"),
    ("json/internal/internal_sale-advert-schema_v1.1.0.json", "json/fixtures/upsert_sale_advert.json"),
    ("json/internal/internal_sale-advert-schema_v1.0.0.json", "json/fixtures/upsert_sale_advert.json"),
    ("json/internal/internal_delete-sale-advert-schema_v1.0.0.json", "json/fixtures/delete_sale_advert.json"),
    ("json/internal/internal_purge-advert-schema.json", "json/fixtures/purge_advert.json"),
    ("json/public/public_sale-advert-schema_v1.1.0.json", "json/public/examples/public_sale-advert-schema_v1.1.0-example.json"),
    ("json/public/public_sale-advert-schema_v1.0.0.json", "json/public/examples/public_sale-advert-schema_v1.0.0-example.json"),
    ("json/public/simplified_export_sale-advert-schema_v1.0.0.json", "json/fixtures/simplified_export_sale_advert.json"),
]

# Published, but not reachable from any fixture root — still strictly checked.
EXTRA_ROOTS = [
    "json/public/geo-public-schema_v1.0.0.json",
    "json/internal/advert-schema_v1.0.0.json",
    "json/internal/metadata-schema_v1.0.0.json",
]

# Data files, not schemas: display-label maps, fixtures, examples and notes.
NOT_SCHEMAS = ("-lookup-", "/json/fixtures/", "/json/public/examples/")

failures = []
warnings = []


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


class LocalResolver(RefResolver):
    """Resolve the repo's master-pinned $ref URLs against the working tree."""

    def resolve_remote(self, uri):
        if uri.startswith(PREFIX):
            with open(os.path.join(ROOT, uri[len(PREFIX):])) as handle:
                return json.load(handle)
        return super().resolve_remote(uri)


def load(path):
    with open(path) as handle:
        return json.load(handle)


def json_files():
    for dirpath, _, filenames in os.walk(os.path.join(ROOT, "json")):
        for name in sorted(filenames):
            if name.endswith(".json"):
                yield os.path.join(dirpath, name)


def is_schema(path):
    return not any(marker in rel(path) for marker in NOT_SCHEMAS)


def collect_refs(node, found):
    """Collect every $ref string anywhere in a schema."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            found.add(ref)
        for value in node.values():
            collect_refs(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, found)


print("== 1. the live set: roots plus everything they $ref")
live = {}          # abs path -> parsed schema
pending = [os.path.join(ROOT, p) for p, _ in PAIRS]
pending += [os.path.join(ROOT, p) for p in EXTRA_ROOTS]
seen = set()

while pending:
    path = pending.pop()
    if path in seen:
        continue
    seen.add(path)
    if not os.path.exists(path):
        failures.append(f"{rel(path)} is referenced but does not exist")
        continue
    if os.path.getsize(path) == 0:
        failures.append(f"{rel(path)} is in the live set but is 0 bytes")
        continue
    try:
        live[path] = load(path)
    except json.JSONDecodeError as exc:
        failures.append(f"{rel(path)} is not valid JSON: {exc}")
        continue
    refs = set()
    collect_refs(live[path], refs)
    for ref in refs:
        if not ref.startswith(PREFIX):
            if not ref.startswith("#"):
                warnings.append(f"{rel(path)} has a $ref that is neither local nor a master URL: {ref}")
            continue
        pending.append(os.path.join(ROOT, ref[len(PREFIX):]))
print(f"   {len(live)} live schema file(s)")

print("\n== 2. every live schema is a valid draft-07 schema")
for path in sorted(live):
    try:
        Draft7Validator.check_schema(live[path])
    except Exception as exc:  # noqa: BLE001 - surface whatever the library raises
        first_line = str(exc).strip().splitlines()[0]
        failures.append(f"{rel(path)} is not a valid draft-07 schema: {first_line}")
print(f"   {len(live)} checked")

print("\n== 3. every fixture validates against its schema")
for schema_rel, doc_rel in PAIRS:
    schema_path = os.path.join(ROOT, schema_rel)
    doc_path = os.path.join(ROOT, doc_rel)
    if schema_path not in live:
        failures.append(f"{schema_rel}: schema missing or unparseable, cannot validate {doc_rel}")
        continue
    try:
        doc = load(doc_path)
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"{doc_rel} could not be read: {exc}")
        continue
    schema = live[schema_path]
    validator = Draft7Validator(schema, resolver=LocalResolver(base_uri=PREFIX, referrer=schema))
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    status = "ok" if not errors else f"{len(errors)} error(s)"
    print(f"   {os.path.basename(schema_rel):<48} <- {os.path.basename(doc_rel):<46} {status}")
    for error in errors:
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        failures.append(f"{doc_rel} at {location}: {error.message}")

print("\n== 4. no live schema accepts anything at all")
for path in sorted(live):
    schema = live[path]
    if schema.get("type") != "object" or not schema.get("properties"):
        continue
    if not schema.get("required") and schema.get("additionalProperties") is not False:
        warnings.append(
            f"{rel(path)} declares properties but sets no 'required' and leaves "
            "additionalProperties open — it validates any object, including {}"
        )

print("\n== 5. files under json/ that nothing live references")
orphans = []
for path in json_files():
    if path in live or not is_schema(path):
        continue
    orphans.append(path)
    if os.path.getsize(path) == 0:
        warnings.append(f"{rel(path)} is orphaned and 0 bytes")
        continue
    try:
        load(path)
    except json.JSONDecodeError as exc:
        warnings.append(f"{rel(path)} is orphaned and is not valid JSON: {exc}")
print(f"   {len(orphans)} orphaned file(s)")

if warnings:
    print(f"\n-- {len(warnings)} warning(s), not fatal")
    for warning in warnings:
        print(f"   ! {warning}")

if failures:
    print(f"\n== FAILED: {len(failures)} problem(s)")
    for failure in failures:
        print(f"   x {failure}")
    sys.exit(1)

print("\n== PASSED")
