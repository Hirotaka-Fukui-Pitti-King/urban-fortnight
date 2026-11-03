#!/usr/bin/env python3
"""Math quality gate: parse Pandoc AST before PDF, then check rendered PDF + previews."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

RAW_LATEX = re.compile(r"\\(?:frac|sum|beta|Delta|mathbb|mathcal|mathrm|left|right|geq|leq|varphi|langle|rangle|partial|lambda|alpha)\b")
PDF_SYMBOLS = ("∑", "Δ", "⟨", "≥")
EXCLUDED = {".git",".quarto","_freeze","_site","node_modules","venv",".venv","__pycache__"}

class MathQualityError(ValueError):
    """A source or rendered PDF does not satisfy math invariants."""

def command(*args: str) -> str:
    result=subprocess.run(args,capture_output=True,text=True,check=False)
    if result.returncode:
        raise MathQualityError(f"Command {args!r} failed: {result.stderr[-1500:]}")
    return result.stdout

def walk(node):
    if isinstance(node,dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node,list):
        for value in node:
            yield from walk(value)

def check_braces(math: str, label: str) -> None:
    depth=0
    for i,char in enumerate(math):
        if char not in "{}" or (i>0 and math[i-1]=="\\"):
            continue
        depth+=1 if char=="{" else -1
        if depth<0:
            raise MathQualityError(f"{label}: closing math brace without opening")
    if depth:
        raise MathQualityError(f"{label}: unclosed math brace")
    if len(re.findall(r"\\left\b",math))!=len(re.findall(r"\\right\b",math)):
        raise MathQualityError(f"{label}: unpaired \\left / \\right")

def math_inventory(source: Path) -> dict[str,int]:
    lines=source.read_text(encoding="utf-8").splitlines()
    bad=[i for i,line in enumerate(lines,1) if line.strip()=="$"]
    if bad:
        raise MathQualityError(f"{source}: single-dollar math fence lines {bad}; use $$")
    boundaries=[i for i,line in enumerate(lines,1) if line.strip()=="$$"]
    if len(boundaries)%2:
        raise MathQualityError(f"{source}: odd number of display math fences")
    for start,end in zip(boundaries[::2],boundaries[1::2]):
        body="\n".join(lines[start:end-1]).strip()
        if not body or "$" in body:
            raise MathQualityError(f"{source}:{start}: empty or malformed display math")
    pandoc=("pandoc",) if shutil.which("pandoc") else ("quarto","pandoc")
    ast=json.loads(command(*pandoc,"--from","markdown+tex_math_dollars+raw_tex",
                           "--to","json",str(source)))
    counts=Counter()
    stray=[]
    for node in walk(ast.get("blocks",[])):
        if node.get("t")=="Math":
            kind,formula=node["c"]
            counts[kind["t"]]+=1
            check_braces(formula,str(source))
        if node.get("t")=="Str" and "$" in node.get("c",""):
            stray.append(node["c"])
        if node.get("t") in ("RawInline","RawBlock"):
            fmt,raw=node["c"]
            if fmt in ("tex","latex") and RAW_LATEX.search(raw):
                raise MathQualityError(f"{source}: math TeX outside math mode: {raw[:100]}")
    if stray:
        raise MathQualityError(f"{source}: Pandoc left raw dollar tokens in prose: {stray[:5]}")
    if counts["DisplayMath"]!=len(boundaries)//2:
        raise MathQualityError(
            f"{source}: {len(boundaries)//2} display fences but "
            f"{counts['DisplayMath']} Pandoc display-math nodes")
    return {"display":counts["DisplayMath"],"inline":counts["InlineMath"]}

def discover_qmd(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.qmd")
                  if not set(p.relative_to(root).parts).intersection(EXCLUDED))

def validate_source(root: Path,manifest_path: Path) -> dict:
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version")!=1:
        raise MathQualityError("Bad math manifest schema")
    declared=manifest["documents"]
    files=discover_qmd(root)
    actual_paths={p.relative_to(root).as_posix() for p in files}
    if set(declared)!=actual_paths:
        raise MathQualityError(f"Math inventory does not cover all QMD: "
                               f"new={sorted(actual_paths-set(declared))}, "
                               f"missing={sorted(set(declared)-actual_paths)}")
    for path in files:
        key=path.relative_to(root).as_posix()
        actual=math_inventory(path)
        expected={k:declared[key][k] for k in ("display","inline")}
        if actual!=expected:
            raise MathQualityError(f"{key}: Pandoc math count {actual} differs from "
                                   f"committed manifest {expected}. Review the change and "
                                   "update the manifest if equations changed intentionally.")
        print(f"PASS {key}: {actual['display']} display and {actual['inline']} inline equations")
    return manifest

def validate_pdf(path: Path, target: dict) -> None:
    if not path.is_file() or path.stat().st_size<2000:
        raise MathQualityError(f"Missing/truncated PDF: {path}")
    content=command("pdftotext","-layout",str(path),"-")
    if "$" in content or RAW_LATEX.search(content):
        idx=content.find("$")
        if idx<0:
            idx=RAW_LATEX.search(content).start()
        raise MathQualityError(f"{path}: unconverted TeX source in PDF: "
                               f"{content[max(0,idx-50):idx+130]!r}")
    if len(content)<int(target.get("minimum_extracted_chars",100)):
        raise MathQualityError(f"Short/empty PDF text: {path}")
    info=command("pdfinfo",str(path))
    m=re.search(r"^Pages:\s+(\d+)",info,re.M)
    if not m:
        raise MathQualityError(f"PDF page count missing: {path}")
    pages=int(m.group(1))
    if pages<int(target.get("minimum_pages",1)):
        raise MathQualityError(f"PDF has {pages} pages, below required minimum")
    if target.get("math_font_required"):
        fonts=command("pdffonts",str(path))
        if not re.search(r"(?im)^\S*math\S*\s+",fonts):
            raise MathQualityError(f"{path}: no embedded mathematics font")
        missing=[ch for ch in PDF_SYMBOLS if ch not in content]
        if missing:
            raise MathQualityError(f"{path}: mathematical glyphs missing from PDF text {missing}")
    print(f"PASS PDF {path}: {pages} pages, math/font/text extraction OK")

def render_math_previews(path: Path,folder: Path,max_pages: int=4) -> None:
    folder.mkdir(parents=True,exist_ok=True)
    info=command("pdfinfo",str(path))
    n=int(re.search(r"^Pages:\s+(\d+)",info,re.M).group(1))
    ranking=[]
    for page in range(1,n+1):
        content=command("pdftotext","-f",str(page),"-l",str(page),str(path),"-")
        weight=sum(content.count(ch) for ch in PDF_SYMBOLS)
        weight+=content.count("𝛽")+content.count("𝑄")
        ranking.append((weight,page))
    selected=sorted(page for weight,page in sorted(ranking,reverse=True)[:max_pages]
                    if weight>0)
    if not selected:
        raise MathQualityError(f"Math PDF had no math-heavy preview pages: {path}")
    for page in selected:
        prefix=folder/f"{path.stem}-page-{page:03}"
        command("pdftoppm","-f",str(page),"-l",str(page),"-singlefile",
                "-scale-to","1400","-png",str(path),str(prefix))
        if not prefix.with_suffix(".png").is_file():
            raise MathQualityError(f"Preview was not created for {path} page {page}")
    print(f"Saved math page previews: {selected}")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--manifest",type=Path,default=Path("paper/math-quality-manifest.json"))
    parser.add_argument("--source-check",action="store_true")
    parser.add_argument("--pdf-check",action="store_true")
    parser.add_argument("--preview-dir",type=Path)
    args=parser.parse_args()
    root=args.root.resolve()
    manifest=(validate_source(root,root/args.manifest)
              if args.source_check or not args.pdf_check
              else json.loads((root/args.manifest).read_text(encoding="utf-8")))
    if args.pdf_check:
        for qmd,target in manifest["documents"].items():
            pdf=(root/qmd).with_suffix(".pdf")
            validate_pdf(pdf,target)
            if args.preview_dir and target.get("math_font_required"):
                render_math_previews(pdf,root/args.preview_dir)
if __name__=="__main__":
    try:
        main()
    except (MathQualityError,ValueError,FileNotFoundError) as exc:
        print(f"MATH QUALITY GATE FAILED: {exc}",file=sys.stderr)
        raise SystemExit(1)
