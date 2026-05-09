#!/usr/bin/env python3
"""M3-W2: HistGradientBoosting baseline + permutation importance + top-3 column ablation."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline

from m3_pipeline import FEATURE_COLUMNS, build_preprocessor, prepare_xy
from m3_save import save_training_artifact


def main() -> int:
    p = argparse.ArgumentParser(description="MBV M3-W2: HGBC + permutation importance + ablation.")
    p.add_argument("--train", type=Path, required=True)
    p.add_argument("--val", type=Path, required=True)
    p.add_argument(
        "--n-repeats",
        type=int,
        default=12,
        help="Permutation importance repeats (higher = slower, stabler).",
    )
    p.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="Directory for model.joblib + train_config.yaml (default: <val_dir>/m3_artifacts_boosted).",
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
    use_es = len(X_tr) >= 120
    hgb_kw: dict = {
        "learning_rate": 0.07,
        "max_depth": 7,
        "max_iter": 400,
        "random_state": 42,
        "class_weight": "balanced",
    }
    if use_es:
        hgb_kw["early_stopping"] = True
        hgb_kw["validation_fraction"] = 0.12
        hgb_kw["n_iter_no_change"] = 15
    else:
        hgb_kw["early_stopping"] = False
    hgb = HistGradientBoostingClassifier(**hgb_kw)
    pipe = Pipeline([("prep", prep), ("clf", hgb)])
    pipe.fit(X_tr, y_tr)
    p_va = pipe.predict_proba(X_va)[:, 1]

    ap = average_precision_score(y_va, p_va)
    try:
        auc = roc_auc_score(y_va, p_va)
    except ValueError:
        auc = float("nan")

    r = permutation_importance(
        pipe,
        X_va,
        y_va,
        scoring="average_precision",
        n_repeats=min(args.n_repeats, max(3, len(y_va))),
        random_state=42,
        n_jobs=-1,
    )
    means = r.importances_mean
    order = np.argsort(-means)
    eps = 1e-6
    sig_idx = [int(i) for i in order if means[i] > eps]
    if len(sig_idx) >= 3:
        drop_idx = sig_idx[:3]
    elif sig_idx:
        drop_idx = sig_idx
    else:
        drop_idx = []

    top3_cols = [X_va.columns[i] for i in drop_idx]
    ap_a = float("nan")
    if drop_idx:
        ablated = [c for c in FEATURE_COLUMNS if c not in set(top3_cols)]
        X_tr_a, y_tr_a = prepare_xy(train, ablated)
        X_va_a, y_va_a = prepare_xy(val, ablated)
        prep_a = build_preprocessor(X_tr_a, ablated)
        use_es_a = len(X_tr_a) >= 120
        hgb_a_kw: dict = {
            "learning_rate": 0.07,
            "max_depth": 7,
            "max_iter": 400,
            "random_state": 43,
            "class_weight": "balanced",
        }
        if use_es_a:
            hgb_a_kw["early_stopping"] = True
            hgb_a_kw["validation_fraction"] = 0.12
            hgb_a_kw["n_iter_no_change"] = 15
        else:
            hgb_a_kw["early_stopping"] = False
        hgb_a = HistGradientBoostingClassifier(**hgb_a_kw)
        pipe_a = Pipeline([("prep", prep_a), ("clf", hgb_a)])
        pipe_a.fit(X_tr_a, y_tr_a)
        p_va_a = pipe_a.predict_proba(X_va_a)[:, 1]
        ap_a = average_precision_score(y_va_a, p_va_a)

    lines = [
        "M3 boosted (HistGradientBoostingClassifier, sklearn)",
        f"train labeled n={len(y_tr)}  val labeled n={len(y_va)}",
        f"PR-AUC (val)={ap:.4f}  ROC-AUC={auc:.4f}",
        "",
        "Permutation importance (val, average_precision), top columns:",
    ]
    for rank, i in enumerate(order[:12], start=1):
        col = X_va.columns[i]
        lines.append(f"  {rank:2d}. {col}: mean={means[i]:.5f} std={r.importances_std[i]:.5f}")

    if drop_idx:
        ablation_lines = [
            "",
            f"Ablation: dropped columns with positive permutation mean (up to 3): {top3_cols}",
            f"PR-AUC (val, ablated)={ap_a:.4f}  delta vs full={ap_a - ap:+.4f}",
        ]
    else:
        ablation_lines = ["", "Ablation: skipped (no permutation importance above noise floor)."]
    lines.extend(ablation_lines)
    lines.append("")
    lines.append("Tip: run m3_train_baseline.py on the same parquets for gate sim and m3_threshold_sweep.csv.")
    report = "\n".join(lines)
    print(report)

    out_path = args.val.parent / "m3_boosted_report.txt"
    out_path.write_text(report + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")

    if not args.no_save:
        art = (args.artifact_dir or (args.val.parent / "m3_artifacts_boosted")).resolve()
        n_rep = int(min(args.n_repeats, max(3, len(y_va))))
        cfg = {
            "schema_version": 1,
            "script": "m3_train_boosted.py",
            "model_family": "hist_gradient_boosting",
            "label": "y_profitable",
            "train_parquet": args.train.resolve(),
            "val_parquet": args.val.resolve(),
            "feature_columns": list(FEATURE_COLUMNS),
            "hist_gradient_boosting": dict(hgb_kw),
            "permutation_importance": {"n_repeats": n_rep, "scoring": "average_precision"},
            "ablation_dropped_columns": top3_cols if drop_idx else [],
            "n_train_labeled": int(len(y_tr)),
            "n_val_labeled": int(len(y_va)),
            "val_metrics": {
                "pr_auc": float(ap),
                "roc_auc": float(auc) if auc == auc else None,
                "pr_auc_ablated": float(ap_a) if ap_a == ap_a else None,
            },
            "python": sys.version.split()[0],
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "sklearn_version": sklearn.__version__,
        }
        mp, yp = save_training_artifact(art, pipe, cfg)
        print(f"Wrote {mp}")
        print(f"Wrote {yp}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
