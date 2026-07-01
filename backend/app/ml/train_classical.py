"""Train a classical ML regressor to predict ATS scores.

Compares RandomForestRegressor vs GradientBoostingRegressor, picks the
winner by R² / MAE on a held-out test split, and saves the model + metadata.

Usage:
    python -m app.ml.train_classical

Outputs:
    backend/app/ml/saved_models/ats_score_model.joblib
    backend/app/ml/saved_models/ats_score_model_meta.json
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import sklearn
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.features import FEATURE_NAMES, extract_feature_vector

SEED = 42
DATA_PATH = Path(__file__).resolve().parent / "data" / "training_data.csv"
MODEL_DIR = Path(__file__).resolve().parent / "saved_models"
MODEL_PATH = MODEL_DIR / "ats_score_model.joblib"
META_PATH = MODEL_DIR / "ats_score_model_meta.json"


def _build_features(df: pd.DataFrame) -> np.ndarray:
    """Vectorise every row using extract_feature_vector."""
    vecs = []
    total = len(df)
    for idx, row in enumerate(df.itertuples(index=False)):
        if (idx + 1) % 500 == 0 or idx == 0:
            print(f"  Extracting features … {idx + 1}/{total}")
        vec = extract_feature_vector(row.resume_text, row.jd_text)
        vecs.append(vec)
    return np.vstack(vecs)


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Load data ---------------------------------------------------------
    print(f"Loading training data from {DATA_PATH} …")
    df = pd.read_csv(DATA_PATH)
    print(f"  {len(df)} rows loaded.")

    # ---- Feature extraction ------------------------------------------------
    print("Building feature matrix …")
    t0 = time.time()
    X = _build_features(df)
    y = df["ats_score_label"].values
    feat_time = time.time() - t0
    print(f"  Feature extraction took {feat_time:.1f}s")

    # ---- Train/test split --------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED,
    )
    print(f"  Train: {len(X_train)}  |  Test: {len(X_test)}")

    # ---- Train candidates --------------------------------------------------
    candidates = {
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=200, max_depth=12, random_state=SEED, n_jobs=-1,
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.1, random_state=SEED,
        ),
    }

    results: dict[str, dict] = {}
    for name, model in candidates.items():
        print(f"\nTraining {name} …")
        t0 = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - t0

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = r2_score(y_test, preds)

        results[name] = {
            "model": model,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "train_time": elapsed,
        }
        print(f"  MAE:  {mae:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R²:   {r2:.4f}")
        print(f"  Time: {elapsed:.1f}s")

    # ---- Pick winner -------------------------------------------------------
    best_name = max(results, key=lambda n: results[n]["r2"])
    best = results[best_name]
    print(f"\n★ Winner: {best_name}  (R²={best['r2']:.4f}, MAE={best['mae']:.4f})")

    # ---- Save model --------------------------------------------------------
    joblib.dump(best["model"], MODEL_PATH)
    print(f"  Model saved → {MODEL_PATH}")

    # ---- Save metadata -----------------------------------------------------
    meta = {
        "model_type": best_name,
        "feature_names": FEATURE_NAMES,
        "n_features": len(FEATURE_NAMES),
        "sklearn_version": sklearn.__version__,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "training_rows": len(df),
        "test_size": len(X_test),
        "metrics": {
            "mae": round(best["mae"], 6),
            "rmse": round(best["rmse"], 6),
            "r2": round(best["r2"], 6),
        },
        "all_candidates": {
            name: {
                "mae": round(r["mae"], 6),
                "rmse": round(r["rmse"], 6),
                "r2": round(r["r2"], 6),
            }
            for name, r in results.items()
        },
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved → {META_PATH}")


if __name__ == "__main__":
    main()
