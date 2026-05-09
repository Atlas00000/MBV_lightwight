#!/usr/bin/env python3
"""M3-W1: logistic baseline + optional calibration; M3-W3: threshold sweep CSV."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline

from m3_metrics import threshold_sweep_table
from m3_pipeline import (
    FEATURE_COLUMNS,
    align_proba_to_val,
    build_preprocessor,
    gate_pnl,
    prepare_xy,
)
from m3_save import save_training_artifact


def _cv_splits(n: int) -> int:
    if n < 24:
        return 2
    return min(5, max(3, n // 25))


def main() -> int:
    p = argparse.ArgumentParser(description="MBV M3: logistic baseline, calibration, threshold sweep.")
    p.add_argument("--train", type=Path, required=True, help="Path to train.parquet")
    p.add_argument("--val", type=Path, required=True, help="Path to val.parquet")
    p.add_argument("--threshold", type=float, default=0.5, help="Prob threshold for gate_pnl summary line.")
    p.add_argument(
        "--calibration",
        choices=("none", "sigmoid", "isotonic"),
        default="sigmoid",
        help="Probability calibration on train (CV). Use 'none' to disable.",
    )
    p.add_argument(
        "--min-train-cal",
        type=int,
        default=24,
        help="Minimum labeled train rows to run calibration (else train uncalibrated LR only).",
    )
    p.add_argument(
        "--no-threshold-csv",
        action="store_true",
        help="Skip writing m3_threshold_sweep.csv next to val.",
    )
    p.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="Directory for model.joblib + train_config.yaml (default: <val_dir>/m3_artifacts_baseline).",
    )
    p.add_argument(
        "--no-save",
        action="store_true",
        help="Skip writing model.joblib and train_config.yaml.",
    )
    args = p.parse_args()

    train = pd.read_parquet(args.train)
    val = pd.read_parquet(args.val)

    X_tr, y_tr = prepare_xy(train)
    X_va, y_va = prepare_xy(val)

    prep = build_preprocessor(X_tr)
    clf = LogisticRegression(
        max_iter=500,
        class_weight="balanced",
        random_state=42,
        solver="lbfgs",
    )
    pipe_uncal = Pipeline([("prep", prep), ("clf", clf)])
    pipe_uncal.fit(X_tr, y_tr)
    p_va_unc = pipe_uncal.predict_proba(X_va)[:, 1]

    use_cal = args.calibration != "none" and len(y_tr) >= args.min_train_cal
    cal_cv: int | None = None
    if use_cal:
        cal_cv = min(_cv_splits(len(y_tr)), max(2, len(y_tr) // 3))
        cal_pipe = CalibratedClassifierCV(
            clone(pipe_uncal),
            method=args.calibration,
            cv=cal_cv,
        )
        cal_pipe.fit(X_tr, y_tr)
        p_va = cal_pipe.predict_proba(X_va)[:, 1]
        cal_label = f"{args.calibration} (cv={cal_cv})"
        pipe_final = cal_pipe
    else:
        p_va = p_va_unc
        cal_label = "disabled"
        pipe_final = pipe_uncal

    proba_full = align_proba_to_val(val, p_va)

    ap = average_precision_score(y_va, p_va)
    try:
        auc = roc_auc_score(y_va, p_va)
    except ValueError:
        auc = float("nan")
    brier = brier_score_loss(y_va, p_va)
    brier_unc = brier_score_loss(y_va, p_va_unc)
    maj = float(np.mean(y_va >= 0.5))
    brier_base = brier_score_loss(y_va, np.full_like(p_va, maj, dtype=float))

    n_bins = max(3, min(8, len(y_va) // 3))
    ece_line = ""
    if len(y_va) >= n_bins * 2:
        prob_true, prob_pred = calibration_curve(y_va, p_va, n_bins=n_bins, strategy="uniform")
        ece = float(np.mean(np.abs(prob_true - prob_pred)))
        ece_line = f"Approx ECE (uniform {n_bins} bins)={ece:.4f}"

    gate = gate_pnl(val, proba_full, args.threshold)

    lines = [
        "M3 baseline (logistic regression)",
        f"train labeled n={len(y_tr)}  val labeled n={len(y_va)}",
        f"Calibration: {cal_label}",
        f"PR-AUC (average_precision)={ap:.4f}",
        f"ROC-AUC={auc:.4f}",
        f"Brier (model)={brier:.4f}  Brier (uncalibrated LR)={brier_unc:.4f}  Brier (majority p={maj:.3f})={brier_base:.4f}",
    ]
    if ece_line:
        lines.append(ece_line)
    lines.extend(
        [
            "",
            f"Gate sim (val, executed==1 & has out_pnl): n={int(gate['n'])}",
            f"  sum(out_pnl) all={gate['all_sum']:.4f}",
            f"  sum(out_pnl) if p>={args.threshold}={gate['gate_sum']:.4f}",
        ]
    )

    report = "\n".join(lines)
    print(report)

    out_dir = args.val.parent
    (out_dir / "m3_baseline_report.txt").write_text(report + "\n", encoding="utf-8")
    print(f"Wrote {out_dir / 'm3_baseline_report.txt'}")

    if not args.no_threshold_csv:
        thr = np.concatenate([[0.01, 0.02, 0.03], np.arange(0.05, 1.0, 0.05)])
        tbl = threshold_sweep_table(val, proba_full, thr)
        csv_path = out_dir / "m3_threshold_sweep.csv"
        tbl.to_csv(csv_path, index=False)
        print(f"Wrote {csv_path} ({len(tbl)} rows)")

    if not args.no_save:
        art = (args.artifact_dir or (args.val.parent / "m3_artifacts_baseline")).resolve()
        cfg = {
            "schema_version": 1,
            "script": "m3_train_baseline.py",
            "model_family": "logistic_regression",
            "label": "y_profitable",
            "train_parquet": args.train.resolve(),
            "val_parquet": args.val.resolve(),
            "feature_columns": list(FEATURE_COLUMNS),
            "calibration": {
                "method": args.calibration if use_cal else "none",
                "cv_folds": cal_cv,
                "min_train_rows": int(args.min_train_cal),
                "applied": bool(use_cal),
            },
            "logistic_regression": {
                "max_iter": 500,
                "class_weight": "balanced",
                "solver": "lbfgs",
                "random_state": 42,
            },
            "default_gate_threshold": float(args.threshold),
            "n_train_labeled": int(len(y_tr)),
            "n_val_labeled": int(len(y_va)),
            "val_metrics": {
                "pr_auc": float(ap),
                "roc_auc": float(auc) if auc == auc else None,
                "brier": float(brier),
                "brier_uncalibrated_lr": float(brier_unc),
            },
            "python": sys.version.split()[0],
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "sklearn_version": sklearn.__version__,
        }
        mp, yp = save_training_artifact(art, pipe_final, cfg)
        print(f"Wrote {mp}")
        print(f"Wrote {yp}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
