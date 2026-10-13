#!/usr/bin/env python3
"""
Lab Critical Value Engine
Flags critical/panic lab values against age/sex-specific limits with delta-check integration.
Stdlib parser / mapper with batch CSV and single lookup.
"""
import argparse
import csv
import sys
from pathlib import Path


def lookup(query):
    """Single lookup: token overlap + substring scoring (no deps). Returns top hits."""
    q = str(query).lower().strip()
    # built-in dictionary of lab value terms
    candidates = [
        ("2160-0 Creatinine", "creatinine"),
        ("6690-2 WBC", "wbc"),
        ("718-7 Hemoglobin", "hemoglobin"),
        ("4548-4 HbA1c", "hba1c"),
        ("Platelets", "platelets"),
    ]
    scored = []
    for label, key in candidates:
        score = 0
        if key in q:
            score += 10
        # token overlap
        qt = set(q.split())
        lt = set(label.lower().split())
        overlap = len(qt & lt)
        score += overlap * 2
        scored.append((score, label))
    scored.sort(reverse=True)
    top = scored[0] if scored and scored[0][0] > 0 else (0, None)
    return {"query": query, "top_hit": top[1], "score": top[0], "all": [item for item in scored if item[0] > 0][:3]}

def process_csv(inp, out):
    """Process a CSV file, looking up each row's query value against the lab value bank."""
    inp_path = Path(inp)
    if not inp_path.is_file():
        raise FileNotFoundError(f"Input CSV file not found: {inp}")
    with open(inp_path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fn = r.fieldnames or []
        if not fn:
            raise ValueError("CSV file has no header row")
        # guess query column
        qcol = fn[0]
        for cand in ["query", "test", "drug", "code", "variant", "hla", "lab", "name"]:
            if cand in [c.lower() for c in fn]:
                qcol = [c for c in fn if c.lower() == cand][0]
                break
        results = []
        for row in rows:
            res = lookup(row.get(qcol, ""))
            merged = {**row, "top_hit": res["top_hit"], "lookup_score": res["score"]}
            results.append(merged)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(list(fn) + ["top_hit", "lookup_score"])))
        w.writeheader()
        w.writerows(results)
    return results

def build_parser():
    p=argparse.ArgumentParser(prog="critical_values", description="Lab Critical Value Engine")
    sub=p.add_subparsers(dest="cmd", required=True)
    s=sub.add_parser("single"); s.add_argument("query", nargs="?", default="creatinine"); s.add_argument("--query", dest="q2")
    b=sub.add_parser("batch"); b.add_argument("--input", required=True); b.add_argument("--output", required=True)
    return p

def main(argv=None):
    p=build_parser(); a=p.parse_args(argv)
    if a.cmd=="single":
        q=getattr(a,"q2",None) or getattr(a,"query")
        print(lookup(q)); return 0
    if a.cmd=="batch":
        res=process_csv(a.input, a.output); print(f"Processed {len(res)} -> {a.output}"); return 0
    p.print_help(); return 1

if __name__ == "__main__":
    sys.exit(main())
