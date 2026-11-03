"""Automated page-by-page QA for Typst/Quarto PDFs (not a substitute for human reading).

Usage:
  python lectures/economics-first/scripts/check_pdf_render.py \
    --directory lectures/economics-first \
    --snapshots lectures/economics-first/pdf-qa-snapshots
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

import fitz
import numpy as np

STEMS = (
    "01-aiyagari-statistical-mechanics",
    "02-social-interactions-ising",
    "03-monetary-search-boltzmann",
    "04-other-economic-models",
)
RAW_TEX = re.compile(r"\\(?:frac|dfrac|boxed|begin|end|mathrm|mathcal|partial|underbrace)\b")


def check_pdf(pdf: Path, destination: Path) -> dict:
    if not pdf.is_file() or pdf.stat().st_size < 12_000:
        raise AssertionError(f"Missing or suspiciously small PDF: {pdf}")
    document = fitz.open(pdf)
    if len(document) < 2:
        raise AssertionError(f"PDF unexpectedly short: {pdf}: {len(document)} pages")
    texts = []
    page_data = []
    for index, page in enumerate(document):
        text = page.get_text(sort=True)
        texts.append(text)
        bad_tex=RAW_TEX.search(text)
        # Quarto can silently pass malformed display delimiters through as
        # literal dollar signs even when Typst returns exit code 0.
        if "$" in text:
            dollar=text.index("$")
            excerpt=text[max(0,dollar-120):min(len(text),dollar+220)]
            raise AssertionError(
                f"Unrendered math dollar marker on page {index+1}: {pdf}: {excerpt!r}")
        if bad_tex:
            excerpt=text[max(0,bad_tex.start()-160):min(len(text),bad_tex.end()+160)]
            raise AssertionError(
                f"Raw TeX syntax on page {index+1}: {pdf}: {excerpt!r}")
        for block in page.get_text("blocks"):
            if len(block) > 6 and block[6] == 0 and str(block[4]).strip():
                x0,y0,x1,y1 = block[:4]
                if (x0 < -1 or y0 < -1 or x1 > page.rect.width + 1
                        or y1 > page.rect.height + 1):
                    raise AssertionError(f"Text overflows page {index + 1}: {pdf}")
        # Render EVERY page; inspect the first/middle/final snapshots in the artifact.
        pix = page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
        image = np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
        nonwhite = float(np.mean(np.any(image[:,:,:3] < 245,axis=2)))
        if nonwhite < .0007:
            raise AssertionError(f"Almost blank rendered page {index + 1}: {pdf}")
        target = destination / f"{pdf.stem}-p{index+1:03d}.png"
        pix.save(target)
        page_data.append({
            "page": index+1, "text_chars": len(text),
            "nonwhite_pixel_share": round(nonwhite,6),
            "snapshot":target.name,
        })
    if sum(map(len,texts)) < 2000:
        raise AssertionError(f"Insufficient extractable text in {pdf}")
    return {
        "pdf":pdf.name,"bytes":pdf.stat().st_size,"pages":len(document),
        "extractable_text_characters":sum(map(len,texts)),
        "pages_rendered":len(page_data),
        "page_stats":page_data,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    parser.add_argument("--snapshots",type=Path,required=True)
    args=parser.parse_args()
    args.snapshots.mkdir(parents=True,exist_ok=True)
    data={}
    for stem in STEMS:
        data[stem]=check_pdf(args.directory/(stem+".pdf"),args.snapshots)
    target=args.snapshots/"qa-results.json"
    target.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:{"pages":v["pages"],"pdf":v["pdf"],
                         "rendered_pages":v["pages_rendered"]}
                      for k,v in data.items()},indent=2))


if __name__=="__main__":
    main()
