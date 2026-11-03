#!/usr/bin/env python3
"""Fail-closed source-provenance audit. Indexed text is not a checked PDF."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

LEVELS = {"metadata": 1, "indexed_text": 2, "pdf_bytes": 3,
          "pdf_pages_rendered": 4, "equations_crosschecked": 5}


def verify_bytes(root: Path, item: dict, context: str, errors: list[str]) -> bool:
    rel, digest = item.get("path"), item.get("sha256")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        errors.append(context + ": missing/unsafe evidence path")
        return False
    path = root / rel
    if not path.is_file():
        errors.append(context + ": required local evidence missing: " + rel)
        return False
    if not isinstance(digest, str) or len(digest) != 64:
        errors.append(context + ": SHA-256 missing")
        return False
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        errors.append(context + ": SHA-256 mismatch")
        return False
    return True


def validate(data: dict, root: Path) -> list[str]:
    errors = []
    if data.get("schema_version") != 1:
        errors.append("registry schema must be version 1")
    sources = data.get("sources", {})
    claims = data.get("claims", [])
    if not isinstance(sources, dict) or not sources:
        return ["source records missing"]
    if not isinstance(claims, list) or not claims:
        return ["claim records missing"]
    for sid, source in sources.items():
        level = source.get("source_level")
        if level not in LEVELS:
            errors.append(sid + ": invalid source verification level")
            continue
        if not source.get("metadata_record") or not source.get("evidence"):
            errors.append(sid + ": missing source provenance explanation")
        pdf = source.get("pdf", {})
        if LEVELS[level] >= 3:
            proof = {"path": pdf.get("local_path"), "sha256": pdf.get("sha256")}
            if verify_bytes(root, proof, sid + " PDF", errors):
                if not (root / proof["path"]).read_bytes().startswith(b"%PDF-"):
                    errors.append(sid + ": evidence does not have a PDF signature")
        if LEVELS[level] >= 4:
            pages = pdf.get("page_image_evidence", [])
            if not pages:
                errors.append(sid + ": rendered page-image proof missing")
            for page in pages:
                if not isinstance(page.get("page_number"), int) or page["page_number"] < 1:
                    errors.append(sid + ": invalid page number")
                verify_bytes(root, page, sid + " page image", errors)
        if LEVELS[level] >= 5:
            equations = pdf.get("human_verified_equations", [])
            if not equations:
                errors.append(sid + ": visually crosschecked equation records missing")
            page_numbers = {p.get("page_number") for p in pdf.get("page_image_evidence", [])}
            for eq in equations:
                if (not eq.get("equation_id") or eq.get("page_number") not in page_numbers
                        or not eq.get("inspector") or not eq.get("checked_at")):
                    errors.append(sid + ": invalid equation-to-page inspection record")
        for link in source.get("candidate_links", []):
            if link.get("verified_direct_download") and LEVELS[level] < 3:
                errors.append(sid + ": link falsely marked as working PDF download")
    ids = set()
    for claim in claims:
        cid = claim.get("id")
        if not cid or cid in ids:
            errors.append("duplicate or empty source claim ID")
        ids.add(cid)
        src = sources.get(claim.get("source_id"))
        req = claim.get("required_level")
        status = claim.get("status")
        if src is None or req not in LEVELS:
            errors.append(str(cid) + ": unknown source or evidence requirement")
            continue
        if status not in ("supported", "pending"):
            errors.append(str(cid) + ": unknown claim status")
        tier = src.get("source_level")
        if tier in LEVELS and status == "supported" and LEVELS[tier] < LEVELS[req]:
            errors.append(str(cid) + ": false verification, insufficient source evidence")
    notice = data.get("required_notice")
    if not isinstance(notice, str) or len(notice) < 50:
        errors.append("mandatory verification disclosure missing")
    else:
        for rel in data.get("notice_paths", []):
            f = root / rel
            if not f.is_file() or notice not in f.read_text(encoding="utf-8"):
                errors.append(rel + ": verification notice missing")
    for rel, expected in data.get("additional_notices", {}).items():
        f = root / rel
        if not f.is_file() or expected not in f.read_text(encoding="utf-8"):
            errors.append(rel + ": additional evidence disclaimer missing")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="research/source_provenance/registry.json")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root) if args.root else Path(__file__).resolve().parents[1]
    path = Path(args.registry)
    if not path.is_absolute():
        path = root / path
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data, root)
    if errors:
        raise SystemExit("SOURCE AUDIT FAILED:\n" + "\n".join("- " + e for e in errors))
    print(f"SOURCE AUDIT PASSED: {len(data['sources'])} sources; {len(data['claims'])} claims.")
    print("Evidence consistency only: text extraction is NOT a visual PDF/equation check.")


if __name__ == "__main__":
    main()
