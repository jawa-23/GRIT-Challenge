
# GRIT - Graph-based Rating Inference over Time
### Next Contest Rating Prediction

## 🏆 Live Leaderboard

[![Leaderboard](https://img.shields.io/badge/View-Leaderboard-blue?style=for-the-badge)](https://jawa-23.github.io/GRIT-Challenge)

---
## 1. Overview

The **GRIT challenge** evaluates models on the task of predicting the **next contest rating** of competitive programmers on CodeForces.

Each contest is represented as a graph snapshot where:
- Nodes correspond to a subset of participating contestants.
- Edges connect contestants with similar ratings at the time of contest beginning.

The task is to predict the `nextRating` of each contestant in an **autoregressive evaluation setting**, where past predictions are used to construct future inputs.

---
## 2. Data
### Data Description
The data is derived from the *Codeforces Competitive History Dataset on Kaggle* and was preprocessed through multiple steps to tailor it to the graph structure and the GRIT challenge.

Each snapshot corresponds to a single contest:
- Nodes represent a subset of participating contestants.
- Edges connect nodes based on their relative ratings when entering the contest.
---

### Node Features

Each node contains the following information:
- **node_id** – a unique identifier for each node in the dataset
- **handle** – serves as the contestant ID (strings were converted into integers for privacy)
- **oldRating** – contestant’s rating when entering contest *i*  
- **rating** – contestant’s rating after contest *i*  
- **num_problems_solved** – number of problems solved in contest *i*  
- **participation_gap** – number of contests since the contestant’s last participation  
- **indicator** – a score that represents how well a participant performed in contest *i*
- **contestant_count** – total number of contestants in contest *i*
- **nextRating** – contestant’s rating in the next contest they participate in (*i+1*) → **target to be predicted**

💡*The intuition behind the indicator feature:*

In the original dataset, each participant’s solved problems were recorded as a list of problem identifiers (for example, "A | B | C"). To use this information as a numerical feature, we created the indicator feature. In Codeforces contests, problems are ordered by increasing difficulty, and we assign each problem a weight using powers of two (1, 2, 4, 8, …) according to this order. The indicator for a participant is computed by summing the weights of all problems they solved. This numeric feature therefore captures both the number of problems solved and their relative difficulty. For example, a participant who solves the harder problems C and D would have a higher indicator score (4 + 8 = 12) than one who solves the easier problems A and B (1 + 2 = 3), even though both solved two problems.

---

### Edge Construction

Edges are constructed according to the following criteria:
Two nodes *(u, v)* are connected if:

$$
\left| \text{oldRating}_u - \text{oldRating}_v \right| < \Delta
$$

- The value of **Δ (delta)** was selected such that the number of edges in any snapshot is less than 30,000.
- If a node does not satisfy the above condition with any other node, it is connected to up to **three nodes** with the smallest rating difference (when possible), to avoid isolated nodes.
---

### Training Data Structure

Each contest snapshot is represented by:
- An adjacency matrix  
- A feature matrix  

Inside the `training/` folder:

#### `nodes.parquet`

Used to construct the **feature matrix** for each contest snapshot.

Format:
contestId, node_id, handle, oldRating, rating, num_problems_solved, participation_gap, indicator, contestants_count, nextRating


#### `edges.parquet`

Used to construct the **adjacency matrix** for each contest snapshot.

Format:
contest_id, src, dst

---

## 3. Testing & Evaluation

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

### Evaluation Metric

##### Mean Absolute Error (MAE)
$$
\mathrm{MAE} = \frac{1}{N} \sum_{i=1}^{N} \left| y_{\text{true}, i} - y_{\text{pred}, i} \right|
$$

---

## 4. Why is GRIT Challenging?

### 1) Error Accumulation

Because evaluation is autoregressive:
- Prediction errors propagate forward.
- Mistakes in early contests affect later predictions.
- Models must remain stable over long horizons.

---

### 2) Inconsistent Participation

Some contestants participate irregularly.
The model must account for the `participation_gap` when predicting the next rating.

---

### 3) Registration Rules

Contestants register for contests before they start.
As long as a contestant registers, they are considered a participant, and the contest affects their rating.
If a contestant registers but does not enter on contest day, their rating may drop as if they participated and solved none.

---
### 4) Missing Values

In a few samples (~ 8% of the training samples), the raw dataset included rating changes but did not include the number of solved problems. This results in rare cases where:

$$
\text{rating} > \text{oldRating}
$$

$$
\text{num\\_problems\\_solved} = 0
$$

Your approach should handle these cases.

---

## 5. Goal

Develop a model that:
- Leverages graph structure within contests  
- Handles irregular participation  
- Remains stable under autoregressive rollout  
- Minimizes MAE on the test set  
---

## 6. Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── publish_leaderboard.yml
│       └── score_submission.yml
├── competition/
│   ├── config.yaml
│   ├── evaluate.py
│   ├── metrics.py
│   ├── render_leaderboard.py
│   └── validate_submission.py
├── data/
│   └── public/
│       ├── sample_submission.csv
│       ├── test_edges.parquet
│       ├── test_nodes.parquet
│       ├── train_edges.parquet
│       └── train_nodes.parquet
├── docs/
│   ├── leaderboard.css
│   ├── leaderboard.csv
│   ├── leaderboard.html
│   └── leaderboard.js
├── encryption/
│   ├── decrypt.py
│   ├── encrypt.py
│   ├── generate_keys.py
│   └── public_key.pem
├── leaderboard/
│   ├── leaderboard.csv
│   ├── leaderboard.md
│   └── update_leaderboard.py
└── submissions/
    └── README.md
├── .DS_Store
├── LICENSE
└── README.md
```
---

## 7. Privacy Protocol

To preserve privacy, private submissions are uploaded in encrypted form using the following protocol:

1. Participants encrypt their predictions file locally using the provided public key (`encryption/public_key.pem`).
2. Only the encrypted submission file is stored in the repository.
3. The private decryption key and test labels are restored from GitHub Secrets via GitHub Actions.
4. Decryption and scoring are performed within the runner environment, and all sensitive files are automatically deleted afterward.
5. Only leaderboard updates are committed to the repository; results are visible on the live leaderboard.
6. The pull request is automatically closed after score calculation.
---
## 8. Submission Procedure

### Submitted Files
You will be submitting two files:
   1) `predictions.csv.enc`
      This is an encrypted format of your predicitions file. Your predicitions file before encryption should be like this:
        `predictions.csv`
        ```
        id,y_pred
        2340,1440
        2341,1200
        ...
        ```
            
      Rules:
        - `id` must match exactly the IDs in `test_nodes.parquet`
        - One row per test node
        - No missing or duplicate IDs
        - y_pred must be a non-negative integer
    
   2) `metadata.json`
      This file should include your team name, your model type (Human, LLM, or Human + LLM), and any notes you want to include on the leaderboard.
        Example `metadata.json`:
        ```json
        {
          "team": "my_team",
          "model": "Human",
          "notes": "This is a test"
        }
        ```
### Steps
1. Fork this repository
2. Train your model locally on the training dataset provided in:
   ```
   data/public/train_nodes.parquet
   data/public/train_edges.parquet
   ```
3. Use your trained model to generate the predictions.csv file for the testing dataset provided in:
   ```
   data/public/test_nodes.parquet
   data/public/test_edges.parquet
   ```
4. Encrypt your predictions.csv using the following command in your cmd:
   ```
   python encryption/encrypt.py predictions.csv encryption/public_key.pem predictions.csv.enc
   ```
5. Create a new folder:
   ```
   submissions/inbox/<team_name>/<run_id>/
   ```
   and upload your `predictions.csv.enc` and `metadata.json` to it.

6. Open a Pull Request to `main`

   The PR will be **automatically scored** and the result will be added to the leaderboard.

---

## 9. Leaderboard

After a PR is scored, the result is added to:
- `leaderboard/leaderboard.csv`
- `leaderboard/leaderboard.md`
---

## 10. Rules

- No external or private data
- No manual labeling of test data
- No modification of evaluation scripts
- Only encrypted predictions are submitted
- Feature Engineering is allowed

Violations may result in disqualification.

---

## 11. References

- **Dataset:** [Codeforces Competitive History](https://www.kaggle.com/datasets/abukanabek/codeforces-competitive-history-dataset/)  
- **Graph Neural Networks:** [BASIRA Lab - Deep Graph Learning Course](https://youtube.com/playlist?list=PLug43ldmRSo14Y_vt7S6vanPGh-JpHR7T&si=LsCm-Wyhcpp7Ljxu)
