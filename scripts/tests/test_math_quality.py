"""Intentionally broken QMD/PDF examples verify the CI quality gate rejects failures."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_paper_math import MathQualityError,math_inventory,validate_source,validate_pdf

GOOD = r'''---
title: "Equations"
---

A household chooses $a$, $m$ and $c$.

$$
V(a,m)=\max_{c,a',m'}\{\log(c)+\beta E[V(a',m')]\}.
$$

Capital and money change together.

$$
c+a'+\phi m'=(1+r)a+\phi m.
$$
'''

class TestMathQualityGate(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        (self.root/"paper").mkdir()
        self.qmd=self.root/"paper/article.qmd"
        self.qmd.write_text(GOOD,encoding="utf-8")
        self.manifest=self.root/"paper/math-quality-manifest.json"
        self.manifest.write_text(json.dumps({"schema_version":1,
            "documents":{"paper/article.qmd":{"display":2,"inline":3}}}))
    def test_good_ast(self):
        self.assertEqual(math_inventory(self.qmd),{"display":2,"inline":3})
        validate_source(self.root,self.manifest)
    def test_single_dollar_fences_fail(self):
        self.qmd.write_text(GOOD.replace("$$","$"))
        with self.assertRaisesRegex(MathQualityError,"single-dollar"):
            validate_source(self.root,self.manifest)
    def test_odd_display_fences_fail(self):
        self.qmd.write_text(GOOD.replace("$$","",1))
        with self.assertRaisesRegex(MathQualityError,"odd number"):
            validate_source(self.root,self.manifest)
    def test_missing_inline_math_fails(self):
        self.qmd.write_text(GOOD.replace("$c$","c"))
        with self.assertRaisesRegex(MathQualityError,"math count"):
            validate_source(self.root,self.manifest)
    def test_tex_outside_math_fails(self):
        self.qmd.write_text(GOOD+"\nA raw \\frac{x}{y} was pasted as prose.\n")
        with self.assertRaisesRegex(MathQualityError,"math TeX outside"):
            validate_source(self.root,self.manifest)
    def test_unbalanced_braces_fail(self):
        self.qmd.write_text(GOOD.replace(r"\beta E[",r"\beta {E["))
        with self.assertRaisesRegex(MathQualityError,"unclosed math brace"):
            validate_source(self.root,self.manifest)
    def test_unmatched_left_right_fails(self):
        self.qmd.write_text(GOOD.replace(r"\log(c)",r"\left(\log(c)"))
        with self.assertRaisesRegex(MathQualityError,"unpaired"):
            validate_source(self.root,self.manifest)
    def test_new_unlisted_qmd_fails(self):
        (self.root/"paper/new-paper.qmd").write_text("Text.")
        with self.assertRaisesRegex(MathQualityError,"does not cover all QMD"):
            validate_source(self.root,self.manifest)
    def test_math_count_regression_fails(self):
        m=json.loads(self.manifest.read_text())
        m["documents"]["paper/article.qmd"]["display"]=1
        self.manifest.write_text(json.dumps(m))
        with self.assertRaisesRegex(MathQualityError,"math count"):
            validate_source(self.root,self.manifest)
    def test_pdf_source_leak_fails(self):
        fake=self.root/"broken.pdf"
        fake.write_bytes(b"%PDF"+b" "*3000)
        def cmd(*args):
            if args[0]=="pdftotext":
                return "Some math appeared as $\\Delta_B$ in PDF " + "x"*200
            if args[0]=="pdfinfo":
                return "Pages: 15\n"
            if args[0]=="pdffonts":
                return "NewCMMath-Book yes yes\n"
            raise AssertionError(args)
        with patch("check_paper_math.command",side_effect=cmd):
            with self.assertRaisesRegex(MathQualityError,"unconverted"):
                validate_pdf(fake,{"minimum_pages":10,
                                   "minimum_extracted_chars":100,
                                   "math_font_required":True})
    def test_missing_pdf_math_font_fails(self):
        fake=self.root/"fontless.pdf"
        fake.write_bytes(b"%PDF"+b" "*3000)
        def cmd(*args):
            if args[0]=="pdftotext":
                return "∑ Δ ⟨ ≥ " + "x"*200
            if args[0]=="pdfinfo":
                return "Pages: 15\n"
            if args[0]=="pdffonts":
                return "Libertinus Serif Regular yes yes\n"
            raise AssertionError(args)
        with patch("check_paper_math.command",side_effect=cmd):
            with self.assertRaisesRegex(MathQualityError,"mathematics font"):
                validate_pdf(fake,{"minimum_pages":10,
                                   "minimum_extracted_chars":100,
                                   "math_font_required":True})

if __name__=="__main__":
    unittest.main()
