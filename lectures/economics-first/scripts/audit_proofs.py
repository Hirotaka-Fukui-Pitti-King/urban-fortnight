"""Structural audit of equations and named propositions in economics-first lectures.

This checker verifies *coverage metadata and proof-section presence*, not the
semantic validity of a mathematical proof. Run from any working directory.
"""
from __future__ import annotations
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"DERIVATION-AND-PROOF-AUDIT.md"
STEMS={
    "I":"01-aiyagari-statistical-mechanics",
    "II":"02-social-interactions-ising",
    "III":"03-monetary-search-boltzmann",
    "IV":"04-other-economic-models",
}
EXPECTED={
    "I":{"I.1","I.2","I.3","I.4","I.5"},
    "II":{"II.1","II.2","II.3","II.4"},
    "III":{"III.1","III.2","III.3","III.4"},
    "IV":{"IV.1","IV.2"},
}
PROPOSITION=re.compile(r"\*\*命題\s*([IVX]+\.\d+)")
UNSUPPORTED_TEX=re.compile(r"\\rm(?:\s|(?=[A-Z]))")


def audit() -> list[str]:
    issues=[]
    ledger=AUDIT.read_text(encoding="utf-8")
    for lecture,stem in STEMS.items():
        text=(ROOT/(stem+".md")).read_text(encoding="utf-8")
        qmd=(ROOT/(stem+".qmd")).read_text(encoding="utf-8")
        if text.count("$$")%2:
            issues.append(f"{stem}: unbalanced display math delimiters")
        if re.search(r"(?m)^\$[ \t]*$",text):
            issues.append(f"{stem}: single-dollar display delimiter")
        if UNSUPPORTED_TEX.search(text):
            issues.append(f"{stem}: deprecated \\\\rm inside formula")
        if not qmd.startswith("---\n") or text.partition("\n\n")[2] != qmd.split("\n---\n",1)[1].lstrip("\n"):
            issues.append(f"{stem}: Markdown/Quarto body mismatch")
        matches=list(PROPOSITION.finditer(text))
        found={match.group(1) for match in matches}
        if found!=EXPECTED[lecture]:
            issues.append(f"{stem}: proposition mismatch {found} versus {EXPECTED[lecture]}")
        for index,match in enumerate(matches):
            endpoint=matches[index+1].start() if index+1<len(matches) else len(text)
            next_heading=re.search(r"(?m)^## ",text[match.end():endpoint])
            if next_heading:
                endpoint=min(endpoint,match.end()+next_heading.start())
            body=text[match.end():endpoint]
            if "**証明。**" not in body:
                issues.append(f"{stem}: missing written proof for {match.group(1)}")
            if match.group(1) not in ledger:
                issues.append(f"{stem}: no audit record for {match.group(1)}")
        # Require original scholarly evidence to be visible in each lecture.
        if "doi.org/" not in text:
            issues.append(f"{stem}: missing primary literature URLs")
    if "| Lecture | Equation / Proposition | Derived From | Assumptions | Proof Location | Verification |" not in ledger:
        issues.append("audit missing standard equation mapping columns")
    return issues


if __name__=="__main__":
    errors=audit()
    if errors:
        print("Proof/derivation structural audit FAILED",file=sys.stderr)
        for error in errors:
            print(" - "+error,file=sys.stderr)
        sys.exit(1)
    print("All declared propositions have written proofs and audit entries.")
    print("This verifies source structure, not mathematical correctness.")
