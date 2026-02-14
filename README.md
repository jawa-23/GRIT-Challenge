
# GRIT - Graph-based Rating Inference over Time
### Next Contest Rating Prediction

---

## 📌 Overview

The **GRIT challenge** evaluates models on the task of predicting the **next contest rating** of competitive programmers on CodeForces.

Each contest is represented as a graph snapshot where:
- Nodes correspond to a subset of participating contestants.
- Edges connect contestants with similar ratings at the time of contest beginning.

The task is to predict the `nextRating` of each contestant in an **autoregressive evaluation setting**, where past predictions are used to construct future inputs.

---

## 📂 Data
### Data Description
The dataset is based on **Codeforces Competitive History from Kaggle**. Multiple preprocessing steps were applied to tailor it to the graph structure and the GRIT challenge.

Each snapshot corresponds to a single contest:
- Nodes represent a subset of participating contestants.
- Edges connect nodes based on their relative ratings when entering the contest.

---

### 🧩 Node Features

Each node contains the following information:
- **node_id** – a unique identifier for each node in the dataset
- **handle** – serves as the contestant ID (strings were converted into integers for privacy)
- **oldRating** – contestant’s rating when entering contest *i*  
- **rating** – contestant’s rating after contest *i*  
- **num_problems_solved** – number of problems solved in contest *i*  
- **nextRating** – contestant’s rating in the next contest they participate in (*i+1*) → **target to be predicted**  
- **participation_gap** – number of contests since the contestant’s last participation  
- **contestant_count** – total number of contestants in contest *i*

---

### 🔗 Edge Construction

Edges are constructed according to the following criteria:
Two nodes *(u, v)* are connected if:

|oldRating_u - oldRating_v| < Δ

- The value of **Δ (delta)** was selected such that the number of edges in any snapshot is less than 30,000.
- If a node does not satisfy the above condition with any other node, it is connected to up to **three nodes** with the smallest rating difference (when possible), to avoid isolated nodes.

---

### 🏗 Training Data Structure

Each contest snapshot is represented by:
- An adjacency matrix  
- A feature matrix  

Inside the `training/` folder:

#### `nodes.parquet`

Used to construct the **feature matrix** for each contest snapshot.

Format:
node_id, handle, contestId,	oldRating, rating,	problems_solved_num, contestants_count, nextRating

#### `edges.parquet`

Used to construct the **adjacency matrix** for each contest snapshot.

Format:
contest_id, src, dst

---

## 🧪 Testing & Evaluation

Model evaluation is performed in an **autoregressive manner**.

#### First Appearance in Test Set

For contestants appearing for the first time in the testing data:

- All features except `nextRating` are available.

---

#### Subsequent Appearances

When a contestant appears again in the testing data, the following features will be set to **-1** (invalid rating):

- `oldRating`
- `rating`

These values must be filled using your model’s previous predictions:

- `rating` at contest *(i−1)* → becomes `oldRating` at contest *(i)*  
- `nextRating` at contest *(i−1)* → becomes `rating` at contest *(i)*  

---

#### 💡 Implementation Hint

You may maintain two dictionaries:

- `old_rate[handle]`
- `current_rate[handle]`

Where:

- `old_rate` stores rating at *(i−1)*
- `current_rate` stores predicted `nextRating` at *(i−1)*

At each contest snapshot in the test set:

- Update these values for participating contestants.
- Use them to fill missing features before making predictions.

---

### 📊 Evaluation Metric

##### Mean Absolute Error (MAE)
MAE = (1/N) * Σ |y_true − y_pred|

---

## ⚠️ Why is GRIT Challenging?

### 1️⃣ Missing Values

In a few samples, the raw dataset included rating changes but did not include the number of solved problems. This results in rare cases where:

rating > oldRating

num_problems_solved = 0

Models must be resilient to these noisy samples.

---

### 2️⃣ Inconsistent Participation

Some contestants participate irregularly.
The model must account for the `participation_gap` when predicting the next rating.

---

### 3️⃣ Registration Rules

Contestants register for contests before they start.
As long as a contestant registers, they are considered a participant, and the contest affects their rating.
If a contestant registers but does not solve any problems, their rating may drop as if they participated and solved none.

---

### 4️⃣ Error Accumulation

Because evaluation is autoregressive:
- Prediction errors propagate forward.
- Mistakes in early contests affect later predictions.
- Models must remain stable over long horizons.

---

## 🎯 Goal

Develop a model that:
- Leverages graph structure within contests  
- Handles irregular participation  
- Remains stable under autoregressive rollout  
- Minimizes MAE on the test set  

---

## Repository Structure

```
.
├── data/
│   ├── public/
│   │   ├── train_edges.parquet
│   │   ├── train_nodes.parquet
│   │   ├── test_edges.parquet
│   │   ├── test_nodes.parquet
│   │   └── sample_submission.csv
│   └── private/
│       └── test_labels.parquet   # never committed (used only in CI)
├── competition/
│   ├── config.yaml
│   ├── validate_submission.py
│   ├── evaluate.py
│   └── metrics.py
├── submissions/
│   ├── README.md
│   └── inbox/
├── leaderboard/
│   ├── leaderboard.csv
│   └── leaderboard.md
└── .github/workflows/
    ├── score_submission.yml
    └── publish_leaderboard.yml
```
---

## Submission Format

Participants submit a **single CSV file**:

**predictions.csv**
```
id,y_pred
n0001,0.92
n0002,0.13
...
```

Rules:
- `id` must match exactly the IDs in `test_nodes.parquet`
- One row per test node
- `y_pred` must be a float in [0,1]
- No missing or duplicate IDs


---

## How to Submit

1. Fork this repository
2. Create a new folder:
```
submissions/inbox/<team_name>/<run_id>/
```
3. Add:
   - `predictions.csv`
   - `metadata.json`

Example `metadata.json`:
```json
{
  "team": "example_team",
  "model": "llm-only",
  "llm_name": "gpt-x",
}
```

4. Open a Pull Request to `main`

The PR will be **automatically scored** and the result posted as a comment.

---

## Leaderboard

After a PR is merged, the submission is added to:
- `leaderboard/leaderboard.csv`
- `leaderboard/leaderboard.md`

Rankings are sorted by **descending score**.

---

## Rules

- No external or private data
- No manual labeling of test data
- No modification of evaluation scripts
- Only predictions are submitted

Violations may result in disqualification.
