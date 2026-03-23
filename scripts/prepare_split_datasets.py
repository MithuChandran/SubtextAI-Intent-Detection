import argparse
import hashlib
import os
from pathlib import Path

import pandas as pd


HIGH_DISSONANCE_INTENTS = {
    "Complain",
    "Criticize",
    "Oppose",
    "Taunt",
}

MEDIUM_DISSONANCE_INTENTS = {
    "Doubt",
    "Flaunt",
    "Prevent",
    "Warn",
}

INTENT_EMOJI_MAP = {
    "Acknowledge": ["\U0001F44C", "\U0001F91D", "\u2705"],
    "Advise": ["\U0001F4A1", "\U0001F9E0", "\u261D\uFE0F"],
    "Agree": ["\U0001F44D", "\U0001F91D", "\u2705"],
    "Apologise": ["\U0001F64F", "\U0001F614", "\U0001F97A"],
    "Arrange": ["\U0001F4C5", "\U0001F5D3\uFE0F", "\u23F0"],
    "Ask for help": ["\U0001F64B", "\U0001F97A", "\U0001F6A8"],
    "Asking for opinions": ["\U0001F914", "\u2753", "\U0001F4AD"],
    "Care": ["\U0001F9E1", "\U0001FAD2", "\U0001F6E1\uFE0F"],
    "Comfort": ["\U0001F979", "\U0001F49B", "\U0001FAD0"],
    "Complain": ["\U0001F644", "\U0001F624", "\U0001F62E\u200D\U0001F4A8"],
    "Confirm": ["\u2705", "\U0001F44C", "\U0001F91D"],
    "Criticize": ["\U0001F928", "\U0001F611", "\U0001F914"],
    "Doubt": ["\U0001F914", "\U0001F928", "\U0001F615"],
    "Emphasize": ["\u2757", "\U0001F4A5", "\U0001F525"],
    "Explain": ["\U0001F4D6", "\U0001F4AC", "\U0001F4A1"],
    "Flaunt": ["\U0001F60E", "\U0001F4B8", "\U0001F48E"],
    "Greet": ["\U0001F44B", "\u2728", "\U0001F60A"],
    "Inform": ["\u2139\uFE0F", "\U0001F4E2", "\U0001F4DD"],
    "Introduce": ["\U0001F44B", "\U0001F91D", "\U0001F4DB"],
    "Invite": ["\U0001F389", "\U0001F4E9", "\U0001F37D\uFE0F"],
    "Joke": ["\U0001F602", "\U0001F923", "\U0001F61C"],
    "Leave": ["\U0001F44B", "\U0001F6AA", "\U0001F3C3"],
    "Oppose": ["\U0001F645", "\U0001F44E", "\u26D4"],
    "Plan": ["\U0001F5FA\uFE0F", "\U0001F4CB", "\U0001F4C5"],
    "Praise": ["\U0001F44F", "\U0001F31F", "\U0001F3C6"],
    "Prevent": ["\U0001F6D1", "\u26A0\uFE0F", "\U0001F6AB"],
    "Refuse": ["\U0001F645", "\U0001F6AB", "\U0001F937"],
    "Taunt": ["\U0001F644", "\U0001F60F", "\U0001F921"],
    "Thank": ["\U0001F64F", "\U0001F49B", "\U0001F44D"],
    "Warn": ["\u26A0\uFE0F", "\U0001F6A8", "\U0001F6D1"],
}

FALLBACK_LOW = ["\U0001F642", "\U0001F44D", "\u2728"]
FALLBACK_MEDIUM = ["\U0001F914", "\u26A0\uFE0F", "\U0001F615"]
FALLBACK_HIGH = ["\U0001F644", "\U0001F624", "\U0001F621"]

RAW_SPLITS = {
    "train": "data/raw/train.tsv",
    "dev": "data/raw/dev.tsv",
    "test": "data/raw/test.tsv",
}


def map_dissonance(intent_label):
    if intent_label in HIGH_DISSONANCE_INTENTS:
        return "High"
    if intent_label in MEDIUM_DISSONANCE_INTENTS:
        return "Medium"
    return "Low"


def stable_pick(options, key):
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def choose_emoji(intent_label, source_id):
    options = INTENT_EMOJI_MAP.get(intent_label)
    if options:
        return stable_pick(options, source_id)

    dissonance_label = map_dissonance(intent_label)
    if dissonance_label == "High":
        return stable_pick(FALLBACK_HIGH, source_id)
    if dissonance_label == "Medium":
        return stable_pick(FALLBACK_MEDIUM, source_id)
    return stable_pick(FALLBACK_LOW, source_id)


def normalize_raw_frame(path):
    df = pd.read_csv(path, sep="\t")
    df["Text"] = df["Text"].fillna("").astype(str)
    df["Label"] = df["Label"].fillna("").astype(str)
    return df


def build_records(df, split_name, label_mode):
    records = []
    for _, row in df.iterrows():
        source_id = f"{split_name}:{row['Dialogue_id']}:{row['Utterance_id']}"
        intent_label = row["Label"].strip()
        dissonance_label = map_dissonance(intent_label)
        label = dissonance_label if label_mode == "dissonance3" else intent_label

        records.append(
            {
                "source_id": source_id,
                "split": split_name,
                "text": row["Text"].strip(),
                "emoji": choose_emoji(intent_label, source_id),
                "label": label,
                "intent_label": intent_label,
                "dissonance_label": dissonance_label,
            }
        )

    return pd.DataFrame(records)


def write_split(output_root, split_name, frame):
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / f"{split_name}.csv"
    frame.to_csv(output_path, index=False)
    print(f"Saved {output_path} with {len(frame)} rows.")


def main():
    parser = argparse.ArgumentParser(description="Prepare split-safe train/dev/test datasets.")
    parser.add_argument(
        "--output_root",
        default="data/processed",
        help="Base directory to write prepared datasets.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root)
    tasks = {
        "dissonance3": output_root / "dissonance3",
        "intent30": output_root / "intent30",
    }

    for split_name, path in RAW_SPLITS.items():
        print(f"Loading {path}...")
        df = normalize_raw_frame(path)
        for label_mode, task_root in tasks.items():
            prepared = build_records(df, split_name, label_mode)
            write_split(task_root, split_name, prepared)


if __name__ == "__main__":
    main()
