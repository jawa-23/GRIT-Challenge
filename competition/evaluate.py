
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
    with open("score.txt", "w") as f:
        f.write(str(score))
    print(f"SCORE={score:.8f}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
