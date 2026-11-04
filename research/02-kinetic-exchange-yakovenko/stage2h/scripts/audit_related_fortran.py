"""Download and inspect Chiu–Molico (2021) public replication Fortran code.

IMPORTANT: This is a DIFFERENT model, not Molico–Zhang (2006) source.
Never report code contents if download/extraction fails.
"""
from __future__ import annotations
import hashlib
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ARCHIVE="https://red-files-public.s3.amazonaws.com/codes/18/18-446/Chiu_Molico_codes.zip"
KEYWORDS=re.compile(r"\b(bargain|nash|interp|value function|bellman|iterat|optimiz|distribut|tolera|converg|quadratur|policy|probabil|newton|brent|bisection|fsolve)\w*", re.I)


def run():
    root=Path(__file__).resolve().parents[1]
    output=root/"results"
    output.mkdir(parents=True,exist_ok=True)
    payload=urllib.request.urlopen(urllib.request.Request(
        ARCHIVE,headers={"User-Agent":"Research-replication-audit/1.0"}),
        timeout=90).read()
    if len(payload)>150_000_000:raise ValueError("Unexpectedly large archive")
    import io
    archive=zipfile.ZipFile(io.BytesIO(payload))
    paths=archive.namelist()
    code=[]
    matches=[]
    for name in paths:
        if name.endswith("/"):continue
        suffix=Path(name).suffix.lower()
        if suffix not in (".f",".f90",".f95",".for",".inc",".txt",".md"):continue
        raw=archive.read(name)
        if len(raw)>8_000_000:continue
        decoded=raw.decode("utf-8",errors="replace")
        lines=decoded.splitlines()
        code.append(dict(path=name,lines=len(lines),bytes=len(raw)))
        for idx,line in enumerate(lines,1):
            if KEYWORDS.search(line):
                matches.append(dict(path=name,line=idx,text=line[:180]))
    report=dict(origin=ARCHIVE,different_economy_from_Molico_Zhang_2006=True,
                archive_sha256=hashlib.sha256(payload).hexdigest(),
                archive_bytes=len(payload),archive_members=len(paths),
                readable_code_files=code,keyword_matches=matches[:300])
    (output/"fortran_source_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print("ARCHIVE_SHA256",report["archive_sha256"])
    print("ARCHIVE_BYTES",len(payload),"FILES",len(code))
    for item in code[:80]:
        print("SOURCE",item["path"],item["lines"])
    for item in matches[:80]:
        print("CODE",item["path"],item["line"],item["text"])
    # Selective read-only excerpts for reproducible methodological review.
    # This is Chiu–Molico (2021) related code, NOT the original Zhang model.
    chosen=("Steady State/src_code/bargprob.f90",
            "Steady State/src_code/dq.f90",
            "Steady State/src_code/mm2020.f90")
    for name in chosen:
        if name not in paths:
            print("MISSING_FORTRAN_SOURCE",name)
            continue
        lines=archive.read(name).decode("utf-8",errors="replace").splitlines()
        if name.endswith("mm2020.f90"):
            keep=list(range(190,min(240,len(lines))))
            keep+=list(range(280,min(310,len(lines))))
            keep+=list(range(355,min(381,len(lines))))
        else:
            keep=list(range(min(100,len(lines))))
        print("FORENSIC_SOURCE_START",name)
        for k in keep:
            print(f"F90:{k+1}: {lines[k][:200]}")
        print("FORENSIC_SOURCE_END",name)
    return report


if __name__=="__main__":
    run()
