"""Deliberately misleading provenance must fail the automated gate."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_source_provenance import validate

DATA = json.loads((ROOT / "research/source_provenance/registry.json").read_text())


class TestSourceProvenance(unittest.TestCase):
    def test_provisional_source_registry_is_consistent(self):
        self.assertEqual([], validate(DATA, ROOT))

    def test_text_only_claim_cannot_certify_equations(self):
        d = copy.deepcopy(DATA)
        d["claims"][2]["status"] = "supported"
        self.assertTrue(any("false verification" in x for x in validate(d, ROOT)))

    def test_pdf_visual_claim_needs_real_binary_and_pages(self):
        d = copy.deepcopy(DATA)
        d["sources"]["molico_zhang_2005"]["source_level"] = "equations_crosschecked"
        e = validate(d, ROOT)
        self.assertTrue(any("evidence path" in x for x in e))
        self.assertTrue(any("page-image proof missing" in x for x in e))
        self.assertTrue(any("equation records missing" in x for x in e))

    def test_dead_link_cannot_be_marked_as_downloaded(self):
        d = copy.deepcopy(DATA)
        d["sources"]["molico_zhang_2005"]["candidate_links"][0]["verified_direct_download"] = True
        self.assertTrue(any("falsely marked" in x for x in validate(d, ROOT)))

    def test_disclosure_cannot_be_removed(self):
        d = copy.deepcopy(DATA)
        d["notice_paths"] = ["nonexistent_file.txt"]
        self.assertTrue(any("verification notice missing" in x for x in validate(d, ROOT)))

    def test_legacy_source_warning_cannot_be_removed(self):
        d = copy.deepcopy(DATA)
        path = next(iter(d["additional_notices"]))
        d["additional_notices"][path] = "untrue source certification"
        self.assertTrue(any("additional evidence disclaimer missing" in x for x in validate(d, ROOT)))

    def test_wrong_hash_cannot_certify_pdf(self):
        d = copy.deepcopy(DATA)
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "fake.pdf").write_bytes(b"%PDF-1.4 not an actual paper")
            d["sources"]["molico_zhang_2005"]["source_level"] = "pdf_bytes"
            d["sources"]["molico_zhang_2005"]["pdf"].update(
                local_path="fake.pdf", sha256="0" * 64)
            self.assertTrue(any("SHA-256 mismatch" in x for x in validate(d, root)))


if __name__ == "__main__":
    unittest.main()
