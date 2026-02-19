import os
import pandas as pd
import sys
import pyarrow
from metrics import MAE

def main(pred_path, label_path):
    preds = pd.read_csv(pred_path).sort_values("id")
    labels = pd.read_parquet(label_path).sort_values("id")

    merged = labels.merge(preds, on="id", how="inner")
    if len(merged) != len(labels):
        raise ValueError("ID mismatch between predictions and labels")

    score = MAE(merged["y_true"], merged["y_pred"])
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"SCORE={score}", file=f)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
