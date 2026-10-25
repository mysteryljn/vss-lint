#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
PATH=re.compile(r"^[A-Z][A-Za-z0-9]*(?:\.[A-Z][A-Za-z0-9]*)+$")
# VSS primitive types include 64-bit integers and double precision floating
# point values.  Omitting them rejects otherwise valid catalogs before they
# can be consumed by downstream tooling.
TYPES={"boolean","uint8","uint16","uint32","uint64","int8","int16","int32","int64","float","double","string"}
def lint(model):
    errors=[]
    if not isinstance(model,dict):
        return ["model must be a JSON object"]
    signals=model.get("signals",[])
    if not isinstance(signals,list):
        return ["signals must be an array"]
    seen=set()
    for i,s in enumerate(signals):
        prefix="signals[%d]"%i
        if not isinstance(s,dict):
            errors.append(prefix+": signal must be an object")
            continue
        path=s.get("path"); name=path.rsplit(".",1)[-1] if isinstance(path,str) and "." in path else ""
        if not isinstance(path,str) or not PATH.match(path): errors.append(prefix+": invalid logical path")
        # JSON paths can be arrays/objects as well as strings.  Invalid
        # values are already reported above; do not use unhashable values as
        # keys in ``seen`` or malformed input would crash the linter.
        if isinstance(path,str):
            if path in seen: errors.append(prefix+": duplicate path "+str(path))
            seen.add(path)
        if not isinstance(s.get("description"),str) or len(s["description"].strip())<8: errors.append(prefix+": description is too short")
        if s.get("datatype") not in TYPES: errors.append(prefix+": unsupported datatype")
        unit=s.get("unit")
        if s.get("datatype") not in ("boolean","string") and (not isinstance(unit,str) or not unit.strip()): errors.append(prefix+": numeric signals require unit")
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
