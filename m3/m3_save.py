"""Persist fitted sklearn estimators + small train_config.yaml next to runs."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import yaml


def _yaml_safe(obj: Any) -> Any:
    if isinstance(obj, np.generic):
        return _yaml_safe(obj.item())
    if isinstance(obj, dict):
        return {str(k): _yaml_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_yaml_safe(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj.resolve())
    if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):
        return str(obj)
    return obj


def save_training_artifact(
    artifact_dir: Path,
    model: Any,
    config: dict[str, Any],
    *,
    model_filename: str = "model.joblib",
    compress: int = 3,
) -> tuple[Path, Path]:
    """Write ``model_filename`` and ``train_config.yaml`` under ``artifact_dir`` (created if missing)."""
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / model_filename
    joblib.dump(model, model_path, compress=compress)
    cfg_out = dict(config)
    cfg_out["artifact_dir"] = str(artifact_dir)
    cfg_out["model_file"] = model_filename
    cfg_out["written_at_utc"] = datetime.now(timezone.utc).isoformat()
    yaml_path = artifact_dir / "train_config.yaml"
    yaml_path.write_text(
        yaml.safe_dump(_yaml_safe(cfg_out), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return model_path, yaml_path
