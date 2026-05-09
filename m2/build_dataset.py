#!/usr/bin/env python3
"""One-shot Milestone 2 build: ingest CSVs -> labels -> time split -> train.parquet / val.parquet."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ingest import check_duplicate_executed_signal_ids, ingest_qc_report, load_glob, sort_by_bar_time
from labels import join_outcomes, labels_summary, outcomes_table, signal_table
from split_qc import leakage_audit_text, monthly_pnl_summary, time_split_signals


def main() -> int:
    p = argparse.ArgumentParser(description="MBV Milestone 2: build train/val parquet from CSV logs.")
    p.add_argument(
        "--input",
        required=True,
        help="Glob of MBV_sig_*.csv (quoted on Windows), e.g. \"C:/.../MBV_sig_EURUSD_*.csv\"",
    )
    p.add_argument(
        "--out-dir",
        default="m2/output",
        help="Directory for train.parquet, val.parquet, qc_report.txt",
    )
    p.add_argument("--train-ratio", type=float, default=0.8, help="Fraction of time-ordered SIGNAL rows for train.")
    p.add_argument(
        "--catastrophic-usd",
        type=float,
        default=1.0,
        help="y_catastrophic = 1 if out_pnl <= -this value (account currency).",
    )
    p.add_argument(
        "--fail-on-dup-signal-id",
        action="store_true",
        help="Exit non-zero if duplicate executed signal_id found.",
    )
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_glob(args.input)
    df = sort_by_bar_time(df)

    dups = check_duplicate_executed_signal_ids(df)
    if dups and args.fail_on_dup_signal_id:
        for m in dups:
            print(m, file=sys.stderr)
        return 2

    sig = signal_table(df)
    out = outcomes_table(df)
    merged = join_outcomes(sig, out, catastrophic_usd=args.catastrophic_usd)
    merged = merged.drop(columns=[c for c in ("pnl", "dur_s", "mfe", "mae", "pos_id", "xdeal") if c in merged.columns], errors="ignore")

    train, val = time_split_signals(merged, train_ratio=args.train_ratio)

    train_path = out_dir / "train.parquet"
    val_path = out_dir / "val.parquet"
    train.to_parquet(train_path, index=False)
    val.to_parquet(val_path, index=False)

    report_lines = [
        ingest_qc_report(df),
        "",
        labels_summary(merged, catastrophic_usd=args.catastrophic_usd),
        "",
        monthly_pnl_summary(merged),
        "",
        leakage_audit_text(),
    ]
    if dups:
        report_lines.insert(0, "WARN duplicate executed signal_id:\n  " + "\n  ".join(dups) + "\n")

    report_path = out_dir / "qc_report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Wrote {train_path} rows={len(train)}")
    print(f"Wrote {val_path} rows={len(val)}")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
