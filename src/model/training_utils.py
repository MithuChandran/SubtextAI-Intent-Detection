import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


DEFAULT_SEED = 42


def load_training_frame(path_or_df):
    if isinstance(path_or_df, pd.DataFrame):
        df = path_or_df.copy()
    else:
        df = pd.read_csv(path_or_df)

    if "text" not in df.columns:
        df["text"] = ""
    if "emoji" not in df.columns:
        df["emoji"] = ""
    if "label" not in df.columns:
        df["label"] = ""

    df["text"] = df["text"].fillna("").astype(str)
    df["emoji"] = df["emoji"].fillna("").astype(str)
    df["label"] = df["label"].fillna("").astype(str)

    if "injection_type" in df.columns:
        df["injection_type"] = df["injection_type"].fillna("").astype(str)

    return df.reset_index(drop=True)


def build_group_ids(df):
    if "source_id" in df.columns:
        return df["source_id"].fillna("").astype(str)

    normalized = (
        df["text"].str.strip().str.lower()
        + "||"
        + df["label"].str.strip().str.lower()
    )

    return normalized.map(
        lambda value: hashlib.sha1(value.encode("utf-8")).hexdigest()
    )


def split_train_eval_dataframes(df, eval_ratio=0.1, seed=DEFAULT_SEED):
    df = load_training_frame(df)
    groups = build_group_ids(df)

    if groups.nunique() < 2:
        raise ValueError("Need at least two unique groups for a leakage-safe split.")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=eval_ratio,
        random_state=seed,
    )
    train_idx, eval_idx = next(splitter.split(df, groups=groups))
    train_df = df.iloc[train_idx].reset_index(drop=True)
    eval_df = df.iloc[eval_idx].reset_index(drop=True)
    return train_df, eval_df


def build_label_maps(*frames):
    labels = sorted(
        {
            label
            for frame in frames
            if frame is not None
            for label in load_training_frame(frame)["label"].unique().tolist()
        }
    )
    label2id = {label: idx for idx, label in enumerate(labels)}
    id2label = {idx: label for label, idx in label2id.items()}
    return labels, label2id, id2label


def save_metrics(output_dir, metrics):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(
            metrics,
            handle,
            indent=2,
            sort_keys=True,
            default=lambda value: value.item() if hasattr(value, "item") else str(value),
        )
