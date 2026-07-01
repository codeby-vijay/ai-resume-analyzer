"""Train the deep-learning ATS score regressor.

Uses sentence-transformers (all-MiniLM-L6-v2) to encode resume/JD pairs,
builds the input tensor [resume_emb, jd_emb, elem_diff, elem_prod], and
trains the ATSScoreRegressor from dl_model.py with early stopping on
validation MAE.

Usage:
    python -m app.ml.train_dl

Outputs:
    backend/app/ml/saved_models/ats_dl_model.pt
    backend/app/ml/saved_models/ats_dl_model_meta.json
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from app.ml.dl_model import ATSScoreRegressor
from app.ml.pipeline import _get_embedder  # reuse the cached loader

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

DATA_PATH = Path(__file__).resolve().parent / "data" / "training_data.csv"
MODEL_DIR = Path(__file__).resolve().parent / "saved_models"
WEIGHTS_PATH = MODEL_DIR / "ats_dl_model.pt"
META_PATH = MODEL_DIR / "ats_dl_model_meta.json"

# Hyper-parameters
BATCH_SIZE = 64
LEARNING_RATE = 1e-3
MAX_EPOCHS = 100
PATIENCE = 10  # early stopping patience
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dim


def _encode_texts(embedder, texts: list[str], batch_size: int = 256) -> np.ndarray:
    """Encode a list of texts into sentence embeddings."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embs = embedder.encode(batch, show_progress_bar=False, convert_to_numpy=True)
        all_embeddings.append(embs)
    return np.vstack(all_embeddings)


def _build_pair_features(
    resume_embs: np.ndarray, jd_embs: np.ndarray,
) -> np.ndarray:
    """Build [resume_emb, jd_emb, elem_diff, elem_prod] matrix."""
    diff = resume_embs - jd_embs
    prod = resume_embs * jd_embs
    return np.hstack([resume_embs, jd_embs, diff, prod])


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")  # CPU-only by design

    # ---- Load data ---------------------------------------------------------
    print(f"Loading training data from {DATA_PATH} …")
    df = pd.read_csv(DATA_PATH)
    print(f"  {len(df)} rows loaded.")

    # ---- Encode texts with sentence-transformers ---------------------------
    embedder = _get_embedder()
    if embedder is None:
        print("ERROR: sentence-transformers model not available. Cannot train DL model.")
        return

    print("Encoding resume texts …")
    t0 = time.time()
    resume_embs = _encode_texts(embedder, df["resume_text"].tolist())
    print(f"  Done in {time.time() - t0:.1f}s")

    print("Encoding JD texts …")
    t0 = time.time()
    jd_embs = _encode_texts(embedder, df["jd_text"].tolist())
    print(f"  Done in {time.time() - t0:.1f}s")

    # ---- Build pair features -----------------------------------------------
    X = _build_pair_features(resume_embs, jd_embs)
    y = df["ats_score_label"].values.astype(np.float32)

    # ---- Train / val split -------------------------------------------------
    n = len(X)
    indices = np.random.RandomState(SEED).permutation(n)
    split = int(0.8 * n)
    train_idx, val_idx = indices[:split], indices[split:]

    X_train = torch.tensor(X[train_idx], dtype=torch.float32)
    y_train = torch.tensor(y[train_idx], dtype=torch.float32)
    X_val = torch.tensor(X[val_idx], dtype=torch.float32)
    y_val = torch.tensor(y[val_idx], dtype=torch.float32)

    train_ds = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

    print(f"  Train: {len(X_train)}  |  Val: {len(X_val)}")
    print(f"  Input dim: {X_train.shape[1]}  (4 × {EMBEDDING_DIM})")

    # ---- Build model -------------------------------------------------------
    model = ATSScoreRegressor(embedding_dim=EMBEDDING_DIM).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # ---- Training loop with early stopping ---------------------------------
    best_val_mae = float("inf")
    best_state = None
    patience_counter = 0
    history: list[dict] = []

    print(f"\nTraining for up to {MAX_EPOCHS} epochs (patience={PATIENCE}) …\n")

    for epoch in range(1, MAX_EPOCHS + 1):
        # -- Train --
        model.train()
        train_losses = []
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            preds = model(xb)
            loss = criterion(preds, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        avg_train_loss = float(np.mean(train_losses))

        # -- Validate --
        model.eval()
        with torch.no_grad():
            val_preds = model(X_val.to(device))
            val_loss = criterion(val_preds, y_val.to(device)).item()
            val_mae = float(torch.mean(torch.abs(val_preds - y_val.to(device))).item())

        history.append({
            "epoch": epoch,
            "train_loss": round(avg_train_loss, 6),
            "val_loss": round(val_loss, 6),
            "val_mae": round(val_mae, 6),
        })

        flag = ""
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            best_state = model.state_dict().copy()
            # deep-copy state dict values
            best_state = {k: v.clone() for k, v in best_state.items()}
            patience_counter = 0
            flag = " ★"
        else:
            patience_counter += 1

        print(
            f"  Epoch {epoch:3d}/{MAX_EPOCHS}  "
            f"train_loss={avg_train_loss:.4f}  "
            f"val_loss={val_loss:.4f}  "
            f"val_mae={val_mae:.4f}{flag}"
        )

        if patience_counter >= PATIENCE:
            print(f"\n  Early stopping at epoch {epoch} (no improvement for {PATIENCE} epochs).")
            break

    # ---- Save best weights -------------------------------------------------
    if best_state is not None:
        torch.save(best_state, WEIGHTS_PATH)
        print(f"\n  Model weights saved → {WEIGHTS_PATH}")
    else:
        print("\n  WARNING: No improvement observed; model not saved.")
        return

    # ---- Final evaluation with best weights --------------------------------
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        val_preds_final = model(X_val.to(device))
        final_mae = float(torch.mean(torch.abs(val_preds_final - y_val.to(device))).item())
        final_rmse = float(torch.sqrt(torch.mean((val_preds_final - y_val.to(device)) ** 2)).item())

    print(f"\n  Final val MAE:  {final_mae:.4f}")
    print(f"  Final val RMSE: {final_rmse:.4f}")

    # ---- Save metadata -----------------------------------------------------
    meta = {
        "model_type": "ATSScoreRegressor (PyTorch)",
        "architecture": "3-layer FFN with ReLU + Dropout",
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dim": EMBEDDING_DIM,
        "input_dim": EMBEDDING_DIM * 4,
        "torch_version": torch.__version__,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "training_rows": len(df),
        "val_size": len(X_val),
        "best_epoch": min(history, key=lambda h: h["val_mae"])["epoch"],
        "total_epochs_run": len(history),
        "metrics": {
            "val_mae": round(final_mae, 6),
            "val_rmse": round(final_rmse, 6),
        },
        "hyperparameters": {
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "max_epochs": MAX_EPOCHS,
            "patience": PATIENCE,
            "dropout": 0.3,
        },
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved → {META_PATH}")


if __name__ == "__main__":
    main()
