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
def _datatype_base(datatype):
    """Return the primitive VSS type, including for a primitive array."""
    if not isinstance(datatype, str):
        return None
    base = datatype[:-2] if datatype.endswith("[]") else datatype
    # Only one [] suffix is valid; a second suffix leaves brackets in base and
    # is rejected here instead of being treated as a valid primitive.
    return base if base in TYPES else None
def lint(model):
    errors=[]
    if not isinstance(model,dict):
        return ["model must be a JSON object"]
    signals=model.get("signals",[])
    if not isinstance(signals,list):
        return ["signals must be an array"]
    if not signals:
        # An empty or truncated catalog cannot provide any signal contract;
        # accepting it as valid would let a CI job report success after an
        # export failure removed every entry.
        return ["signals must not be empty"]
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
        # JSON values may use arrays/objects here.  Checking an unhashable
        # value directly against the set would raise TypeError and abort the
        # entire lint, hiding the malformed signal from callers.
        datatype = s.get("datatype")
        base_datatype = _datatype_base(datatype)
        if base_datatype is None: errors.append(prefix+": unsupported datatype")
        unit=s.get("unit")
        if base_datatype not in ("boolean","string") and (not isinstance(unit,str) or not unit.strip()): errors.append(prefix+": numeric signals require unit")
        if s.get("access") not in ("read","write","readWrite"): errors.append(prefix+": access must be read, write, or readWrite")
        if name.startswith("Is") and s.get("datatype")!="boolean": errors.append(prefix+": Is* signals should be boolean")
    return errors
def main(argv=None):
    p=argparse.ArgumentParser(description="Lint a VSS-like signal catalog"); p.add_argument("model",type=Path); a=p.parse_args(argv)
    try: errors=lint(json.loads(a.model.read_text(encoding="utf-8")))
    # The catalog is an external artifact.  Invalid UTF-8 must be reported as
    # a normal input error instead of leaking a decoder traceback from
    # Path.read_text() and aborting the lint job.
    except (OSError,json.JSONDecodeError,UnicodeError) as e: print("error: "+str(e)); return 2
    if errors: print("\n".join("ERROR "+e for e in errors)); return 1
    print("OK: VSS signal catalog passed"); return 0
if __name__=="__main__": raise SystemExit(main())
