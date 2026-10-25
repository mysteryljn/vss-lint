#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
PATH=re.compile(r"^[A-Z][A-Za-z0-9]*(?:\.[A-Z][A-Za-z0-9]*)+$")
TYPES={"boolean","uint8","uint16","uint32","int8","int16","int32","float","string"}
def lint(model):
    errors=[]; seen=set()
    for i,s in enumerate(model.get("signals",[])):
        prefix="signals[%d]"%i; path=s.get("path"); name=path.rsplit(".",1)[-1] if isinstance(path,str) and "." in path else ""
        if not isinstance(path,str) or not PATH.match(path): errors.append(prefix+": invalid logical path")
        if path in seen: errors.append(prefix+": duplicate path "+str(path))
        seen.add(path)
        if not isinstance(s.get("description"),str) or len(s["description"].strip())<8: errors.append(prefix+": description is too short")
        if s.get("datatype") not in TYPES: errors.append(prefix+": unsupported datatype")
        if s.get("datatype") not in ("boolean","string") and not isinstance(s.get("unit"),str): errors.append(prefix+": numeric signals require unit")
        if s.get("access") not in ("read","write","readWrite"): errors.append(prefix+": access must be read, write, or readWrite")
        if name.startswith("Is") and s.get("datatype")!="boolean": errors.append(prefix+": Is* signals should be boolean")
    return errors
def main(argv=None):
    p=argparse.ArgumentParser(description="Lint a VSS-like signal catalog"); p.add_argument("model",type=Path); a=p.parse_args(argv)
    try: errors=lint(json.loads(a.model.read_text(encoding="utf-8")))
    except (OSError,json.JSONDecodeError) as e: print("error: "+str(e)); return 2
    if errors: print("\n".join("ERROR "+e for e in errors)); return 1
    print("OK: VSS signal catalog passed"); return 0
if __name__=="__main__": raise SystemExit(main())
