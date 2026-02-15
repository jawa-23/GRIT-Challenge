import pandas as pd
import os

lb_path = "leaderboard/leaderboard.csv"
submitter = os.environ["SUBMITTER"]
score = float(os.environ["SCORE"])

# Load existing leaderboard
try:
    df = pd.read_csv(lb_path)
except FileNotFoundError:
    df = pd.DataFrame(columns=["team", "score"])

# Only add new submission if participant not already in leaderboard
if submitter not in df['team'].values:
    df = pd.concat([df, pd.DataFrame([[submitter, score]], columns=["team","score"])])

# Sort ascending by score
df = df.sort_values("score", ascending=True).reset_index(drop=True)

# Competition ranking: ties share rank, next ranks skipped
df['rank'] = df['score'].rank(method='min', ascending=True).astype(int)

# Save updated leaderboard
df.to_csv(lb_path, index=False)

