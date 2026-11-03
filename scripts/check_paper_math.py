#!/usr/bin/env python3
"""Validate QMD block mathematics and catch raw TeX delimiters in the rendered PDF."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess

def validate_source(path: Path) -> None:
    lines=path.read_text(encoding="utf-8").splitlines()
    lone=[i+1 for i,line in enumerate(lines) if line.strip()=="$"]
    if lone:
        raise AssertionError(f"Malformed single-dollar display fences on lines {lone}")
    indices=[i for i,line in enumerate(lines) if line.strip()=="$$"]
    if len(indices)<40 or len(indices)%2:
        raise AssertionError(f"Expected at least 20 paired display equations, got {len(indices)} delimiters")
    for start,end in zip(indices[::2],indices[1::2]):
        body="\n".join(lines[start+1:end]).strip()
        if not body or "$" in body:
            raise AssertionError(f"Invalid display math body at line {start+1}")
    important=[
        r"\Delta_B=",r"\Delta_S=",r"\langle\varphi,Q[f]\rangle",
        r"\sum_m\varphi(m)Q_m[f]",r"Q^{\mathrm{ref}}(f)",
        r"V_i(a_i+\Delta)\geq V_i(a_i)",
        r"G_B(m)=b+",r"Y(K^d,L^d)-C-\delta K^s"]
    src="\n".join(lines)
    for formula in important:
        if formula not in src:
            raise AssertionError(f"Important displayed formula missing: {formula}")
    print(f"Validated {len(indices)//2} properly delimited display equations")

def validate_pdf(path: Path) -> None:
    if not path.is_file():
        raise AssertionError(f"Missing PDF: {path}")
    result=subprocess.run(["pdftotext","-layout",str(path),"-"],
        check=True,capture_output=True,text=True).stdout
    # This paper contains no currency-denominated prose or intended literal dollar signs.
    # Visible dollar signs in the old PDF were malformed TeX block delimiters.
    if "$" in result:
        i=result.index("$")
        raise AssertionError("Malformed TeX math in generated PDF: "
                             +repr(result[max(0,i-70):i+150]))
    if len(result)<8000:
        raise AssertionError("PDF unexpectedly empty or truncated")
    print("PDF text preflight: no raw math delimiters survived rendering")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=Path("paper/article.qmd"))
    parser.add_argument("--pdf",type=Path)
    args=parser.parse_args()
    validate_source(args.source)
    if args.pdf:
        validate_pdf(args.pdf)
