"""PyTorch feed-forward regressor for ATS score prediction.

Architecture:
    Input  = [resume_emb ‖ jd_emb ‖ elem_diff ‖ elem_prod]
             → 4 × embedding_dim  (e.g. 4 × 384 = 1 536 for all-MiniLM-L6-v2)
    Hidden = 3 fully-connected layers with ReLU + Dropout
    Output = single scalar clamped to [0, 100]
"""

from __future__ import annotations

import torch
import torch.nn as nn


class ATSScoreRegressor(nn.Module):
    """Sentence-pair regression network for ATS score prediction."""

    def __init__(self, embedding_dim: int = 384, dropout: float = 0.3) -> None:
        super().__init__()
        input_dim = embedding_dim * 4  # [emb_r, emb_j, diff, prod]

        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: shape (batch, input_dim)

        Returns:
            shape (batch,) — predicted ATS score, clamped to [0, 100].
        """
        out = self.net(x).squeeze(-1)
        return out.clamp(0.0, 100.0)
