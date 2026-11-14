#!/usr/bin/env python3
"""
Command-Line Interface for the OpenQASM 3.0 Transpiler (QC-C2-03).

Usage:
    python transpiler_cli.py <path_to_qasm_file> [--targets qiskit cirq cudaq qniverse] [--verify] [--out-dir <dir>]
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from qnvkit.transpile.api import transpile, SUPPORTED_TARGETS
from qnvkit.qasm.diagnostics import QASMError


def main():
    parser = argparse.ArgumentParser(
        description="OpenQASM 3.0 Transpiler for Qiskit, Cirq, NVIDIA CUDA-Q, and Qniverse QSDK (QC-C2-03)."
    )
    parser.add_argument("source", type=str, help="Path to .qasm file or inline QASM string")
    parser.add_argument(
        "--targets", "-t", nargs="+",
        default=["qiskit", "cirq", "cudaq", "qniverse"],
        choices=list(SUPPORTED_TARGETS.keys()),
        help="One or more target frameworks to transpile to"
    )
    parser.add_argument(
        "--verify", "-v", action="store_true",
        help="Execute generated circuits across frameworks and verify mathematical equivalence against reference simulator"
    )
    parser.add_argument(
        "--out-dir", "-o", type=str, default=None,
        help="Optional directory to save generated Python source files"
    )

    args = parser.parse_args()

    try:
        results = transpile(args.source, targets=args.targets, options={"verify": args.verify})
    except QASMError as e:
        print(f"\n[ERROR] Transpilation failed:\n{e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 70)
    print("   OpenQASM 3.0 Transpiler - Execution Summary (QC-C2-03)")
    print("=" * 70)

    for target, res in results.items():
        rep = res.report
        print(f"\n>> Target: {target.upper()} (Target Version: {rep.target_version})")
        print(f"   Status: {rep.status.upper()}")
        print(f"   Qubits: {rep.metrics.get('num_qubits', 0)} | Clbits: {rep.metrics.get('num_clbits', 0)} | Total Ops: {rep.metrics.get('total_ops', 0)}")
        if rep.warnings:
            print(f"   Warnings ({len(rep.warnings)}):")
            for w in rep.warnings:
                print(f"     - {w}")
        if rep.unsupported_constructs:
            print(f"   Unsupported ({len(rep.unsupported_constructs)}):")
            for u in rep.unsupported_constructs:
                print(f"     - {u}")

        # Verification metrics
        ver = rep.metrics.get("cross_framework_verification")
        if ver and "frameworks" in ver:
            fw_info = ver["frameworks"].get(target)
            if fw_info:
                if fw_info.get("executed"):
                    eq_str = "PASSED" if fw_info.get("equivalent") else "FAILED"
                    fid = fw_info.get("fidelity", 0.0)
                    print(f"   Cross-Framework Equivalence: {eq_str} (Fidelity: {fid:.8f})")
                else:
                    print(f"   Execution note: {fw_info.get('note', fw_info.get('error'))}")

        # Save to output directory if requested
        if args.out_dir:
            out_p = Path(args.out_dir)
            out_p.mkdir(parents=True, exist_ok=True)
            fname = f"{target}_generated.py"
            (out_p / fname).write_text(res.code, encoding="utf-8")
            print(f"   Saved code to: {out_p / fname}")
        else:
            print("-" * 50)
            print("--- Generated Code Preview ---")
            code_lines = res.code.strip().splitlines()
            for line in code_lines[:25]:
                print(line)
            if len(code_lines) > 25:
                print(f"    ... ({len(code_lines) - 25} more lines)")
            print("-" * 50)

    print("\n[SUCCESS] Transpilation completed successfully.\n")


if __name__ == "__main__":
    main()
