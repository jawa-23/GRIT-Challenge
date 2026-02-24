import pandas as pd
import torch
import dgl
import pyarrow
from dgl.dataloading import GraphDataLoader

# --- Configuration ---
# You can perform feature engineering and modify the given features (add, remove, or create new ones derived from them)
FEATURE_COLS = [
    "oldRating",
    "rating",
    "num_problems_solved",
    "participation_gap",
    "indicator",
    "contestants_count"
]

TARGET_COL = "nextRating"

# --- Build per-contest DGL graphs ---
def build_graphs(df_edges, df_nodes):
    """
    df_edges: columns = [contestId, src, dst]
    df_nodes: columns = [contestId, node_id, handle, ..., nextRating]
    """
    graphs = []

    for cid, g_edges in df_edges.groupby("contestId"):
        g_nodes = df_nodes[df_nodes["contestId"] == cid]

        # --- Node IDs and handles ---
        node_ids = g_nodes["node_id"].values
        handles = g_nodes["handle"].values
        id_map = {nid: i for i, nid in enumerate(node_ids)}

        # --- Map edges to local indices ---
        src = g_edges["src"].map(id_map).dropna().astype(int).values
        dst = g_edges["dst"].map(id_map).dropna().astype(int).values
        src = torch.tensor(src, dtype=torch.int64)
        dst = torch.tensor(dst, dtype=torch.int64)

        # --- Create graph ---
        G = dgl.graph((src, dst), num_nodes=len(node_ids))

        # --- Node features X (numeric only) ---
        X = torch.tensor(
            g_nodes.set_index("node_id").loc[node_ids][FEATURE_COLS].values,
            dtype=torch.float32
        )
        G.ndata["x"] = X

        # --- Target ---
        y = torch.tensor(
            g_nodes.set_index("node_id").loc[node_ids][TARGET_COL].values,
            dtype=torch.float32
        )
        G.ndata["y"] = y

        # --- Metadata for tracking ---
        G.ndata["node_id"] = torch.tensor(node_ids) # storing global node_id (It is the node identifier in predictions.csv)
        G.handle_list = handles.tolist()

        graphs.append(G)

    return graphs

# --- Build graphs ---
df_edges = pd.read_parquet("data/public/train_edges.parquet")
df_nodes = pd.read_parquet("data/public/train_nodes.parquet")
graphs = build_graphs(df_edges, df_nodes)

# Example: print X and A of the first graph
G0 = graphs[0]
X0 = G0.ndata["x"]
print("Feature matrix X (numeric features):")
print(X0)
print("Shape:", G0.ndata["x"].shape) # Each row in X corresponds to a node

src, dst = G0.edges()
num_nodes = G0.num_nodes()
A0 = torch.zeros((num_nodes, num_nodes), dtype=torch.float32)
A0[src, dst] = 1.0
print("Adjacency matrix A:")
print(A0.numpy())
print("Shape:", A0.shape)

# --- Batch graphs for GNN training ---
loader = GraphDataLoader(graphs, batch_size=8, shuffle=True)

