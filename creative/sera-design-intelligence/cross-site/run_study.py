#!/usr/bin/env python3
"""Execute a configured Sera cross-site study up to the available stage.

Stages:
1. Run extraction for anchors marked `ready`.
2. Persist execution.json.
3. If every ready case already has STYLE_DNA.json and --mine-if-ready is set,
   run the deterministic cross-site miner.

This runner intentionally does not fabricate STYLE_DNA. Semantic DNA synthesis
remains an Agent step because it contains inferred design meaning.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def load_study(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("anchors"), list):
        raise ValueError("study.json must contain anchors[]")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Sera cross-site study.")
    parser.add_argument("study", help="Path to study.json")
    parser.add_argument("--root", help="sera-design-intelligence root; auto-detected by default")
    parser.add_argument("--mine-if-ready", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--skip-extraction", action="store_true")
    args = parser.parse_args()

    study_path = Path(args.study).expanduser().resolve()
    study = load_study(study_path)
    root = Path(args.root).expanduser().resolve() if args.root else Path(__file__).resolve().parents[1]
    adapter = root / "extraction-engine" / "adapter.py"
    miner = root / "cross-site" / "miner.py"

    if not adapter.exists():
        parser.error(f"Missing adapter: {adapter}")

    ready = [a for a in study["anchors"] if a.get("status") == "ready"]
    skipped = [a for a in study["anchors"] if a.get("status") != "ready"]

    execution: dict[str, Any] = {
        "study_id": study.get("study_id"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "anchors": [],
        "skipped": [{"id": a.get("id"), "status": a.get("status")} for a in skipped],
        "semantic_dna_synthesis_required": True,
    }

    extraction_failed = False
    for anchor in ready:
        case_id = anchor["id"]
        case_root = root / anchor["case_path"]
        raw_dir = case_root / "raw" / "designlang"
        dna_file = case_root / "dna" / "STYLE_DNA.json"

        item = {
            "id": case_id,
            "url": anchor["url"],
            "case_path": str(case_root),
            "raw_dir": str(raw_dir),
            "dna_ready_before_run": dna_file.exists(),
        }

        if not args.skip_extraction:
            cmd = [sys.executable, str(adapter), anchor["url"], "--out", str(raw_dir)]
            result = run(cmd, root)
            item["extraction_exit_code"] = result.returncode
            item["extraction_stdout_tail"] = result.stdout[-2000:]
            item["extraction_stderr_tail"] = result.stderr[-2000:]
            if result.returncode != 0:
                extraction_failed = True
                execution["anchors"].append(item)
                if not args.continue_on_error:
                    break
                continue
        else:
            item["extraction_exit_code"] = None
            item["extraction_skipped"] = True

        item["dna_ready_after_run"] = dna_file.exists()
        execution["anchors"].append(item)

    execution["finished_at"] = datetime.now(timezone.utc).isoformat()
    execution["extraction_complete"] = not extraction_failed and len(execution["anchors"]) == len(ready)

    execution_path = study_path.parent / "execution.json"
    execution_path.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    all_dna = bool(ready) and all((root / a["case_path"] / "dna" / "STYLE_DNA.json").exists() for a in ready)
    if args.mine_if_ready and all_dna:
        out = study_path.parent / "result.json"
        md = study_path.parent / "result.md"
        cmd = [sys.executable, str(miner)]
        for anchor in ready:
            cmd += ["--case", f"{anchor['id']}={root / anchor['case_path']}"]
        cmd += ["--out", str(out), "--markdown", str(md)]
        result = run(cmd, root)
        execution["mining_exit_code"] = result.returncode
        execution["mining_stdout"] = result.stdout
        execution["mining_stderr"] = result.stderr
        execution_path.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result.returncode

    if not all_dna:
        print("Extraction stage recorded. Next: synthesize evidence-backed STYLE_DNA.json for each ready anchor.")
    elif not args.mine_if_ready:
        print("All STYLE_DNA files exist. Re-run with --mine-if-ready to generate cross-site candidates.")

    return 1 if extraction_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
