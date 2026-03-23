import pandas as pd
import random
import argparse
import os
from transformers import pipeline
from tqdm import tqdm

# --- CONFIGURATION ---
DATA_PATH = "data/raw/train.tsv"
OUTPUT_DIR = "data/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- EMOJI MAPS (A/B TEST) ---

# PLAN A: STANDARD (~50 Emojis)
# Focus: High-frequency, clear signals.
CONSONANT_MAP_50 = {
    "POSITIVE": ["❤️", "😊", "👍", "🔥", "😂", "🥰", "✨", "🙌", "🥂", "💯"],
    "NEGATIVE": ["😢", "😡", "👎", "💔", "😞", "😭", "😠", "🤦", "🥀", "😩"]
}
DISSONANT_MAP_50 = {
    "POSITIVE": ["😒", "🙄", "💀", "🙃", "😐"], 
    "NEGATIVE": ["😅", "😊", "😇", "🙂", "👋"]
}
SOCIAL_MAP_50 = {
    "Flaunt": ["💅", "💸", "👑", "🚀"],
    "Taunt": ["🙃", "👏", "🤡", "🤣"],
    "Complaint": ["🙄", "😤", "🤦‍♀️", "😑"]
}

# PLAN B: RICH (~100 Emojis)
# Focus: Nuance and specific intents.
CONSONANT_MAP_100 = {
    "POSITIVE": ["❤️", "😊", "👍", "🔥", "😂", "🥰", "✨", "🙌", "🥂", "💯", "🤩", "💖", "🎉", "👏", "💪", "🌈", "🎈", "🤗", "😎", "💐"],
    "NEGATIVE": ["😢", "😡", "👎", "💔", "😞", "😭", "😠", "🤦", "🥀", "😩", "😫", "🤬", "😤", "🤢", "🤕", "🤐", "🥺", "😿", "😣", "📉"]
}
DISSONANT_MAP_100 = {
    "POSITIVE": ["😒", "🙄", "💀", "🙃", "😐", "🤥", "🥱", "😬", "😏", "😑", "🧐", "🤐", "🌚", "🎭", "😶"], 
    "NEGATIVE": ["😅", "😊", "😇", "🙂", "👋", "😘", "💅", "🍵", "🤠", "🤪", "🐒", "🤷", "🧘", "💫", "🦄"]
}
SOCIAL_MAP_100 = {
    "Flaunt": ["💅", "💸", "👑", "🚀", "💎", "🍸", "🤑", "🚁", "🏰", "🥂"],
    "Taunt": ["🙃", "👏", "🤡", "🤣", "🍼", "🗑️", "🎻", "🧂", "🤌", "🤥"],
    "Comfort": ["🫂", "🥺", "💙", "🌺", "🩹", "❤️‍🩹", "🧸", "🍵", "🤗", "🕯️"],
    "Praise": ["👏", "🌟", "🥂", "💯", "🏆", "👑", "💐", "🏅", "🔥", "🙌"],
    "Care": ["🤲", "💝", "🍵", "🧣", "🧸", "💌", "🍲", "🩹", "🛡️", "🤝"],
    "Confirm": ["🤝", "✅", "👌", "🫡", "👍", "🆗", "☑️", "🤙", "🤘", "🤛"],
    "Advise": ["☝️", "🧠", "💡", "🗒️", "🧐", "📚", "🧭", "⚖️", "📢", "🔮"],
    "Warn": ["⚠️", "🚩", "🛑", "🤫", "☠️", "🚫", "☢️", "🚨", "🚷", "🙅"],
    "Criticize": ["😒", "🤏", "🤦‍♂️", "🙄", "📉", "🚮", "💩", "🥀", "😐", "😑"],
    "Complaint": ["🙄", "😤", "🤦‍♀️", "😑", "💤", "😫", "🤯", "🤬", "🗯️", "🐌"],
    "Introduce": ["👋", "🤝", "✨", "🆕", "📛", "🙋", "🎙️", "🎫", "👶", "🐣"],
    "Inform": ["ℹ️", "📢", "📎", "🤔", "💡", "📡", "📰", "🔔", "📣", "📝"],
    "Ask for help": ["🆘", "🙋", "🙏", "🏳️", "🚑", "🛟", "🤝", "🥺", "🔋", "🪜"],
    "Apologise": ["🙇", "🏳️", "😓", "🥀", "🤐", "🙏", "💧", "💔", "🤕", "😶"]
}

# --- INJECTOR CLASS ---
class EmojiInjector:
    def __init__(self, mode="standard"):
        self.mode = mode
        print(f"Initializing Injector in {mode.upper()} mode...")
        self.sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        if mode == "rich":
            self.consonant_map = CONSONANT_MAP_100
            self.dissonant_map = DISSONANT_MAP_100
            self.social_map = SOCIAL_MAP_100
        else:
            self.consonant_map = CONSONANT_MAP_50
            self.dissonant_map = DISSONANT_MAP_50
            self.social_map = SOCIAL_MAP_50

    def get_consonant(self, text):
        try:
            result = self.sentiment_pipe(text[:512])[0]
            emoji = random.choice(self.consonant_map.get(result['label'], ["🙂"]))
            return emoji
        except:
            return "🙂"

    def get_dissonant(self, text, label):
        if label in ["Complaint", "Criticize"]:
            return random.choice(self.dissonant_map["NEGATIVE"])
        
        try:
            pred = self.sentiment_pipe(text[:512])[0]
            if pred['label'] == "NEGATIVE":
                return random.choice(self.dissonant_map["NEGATIVE"])
            elif pred['label'] == "POSITIVE":
                return random.choice(self.dissonant_map["POSITIVE"])
        except:
            pass
        return "😶"

    def get_social(self, label):
        return random.choice(self.social_map[label]) if label in self.social_map else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["standard", "rich"], default="standard", help="Injector mode: standard (50 emojis) or rich (100 emojis)")
    args = parser.parse_args()

    print("Loading data...")
    try:
        df = pd.read_csv(DATA_PATH, sep='\t')
    except Exception as e:
        print(f"Error reading TSV: {e}")
        return

    # Normalize columns
    if 'Label' not in df.columns or 'Text' not in df.columns:
        df.columns = [c.capitalize() for c in df.columns]

    injector = EmojiInjector(mode=args.mode)
    augmented_data = []

    print(f"Generating dataset for {args.mode} mode...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        text = str(row['Text']).strip()
        label = str(row['Label']).strip()

        # Tier 0: Plain Text
        augmented_data.append({"text": text, "emoji": "", "label": label, "injection_type": "Plain"})

        # Tier 1: Consonant
        augmented_data.append({"text": text, "emoji": injector.get_consonant(text), "label": label, "injection_type": "Consonant"})

        # Tier 2: Dissonant
        augmented_data.append({"text": text, "emoji": injector.get_dissonant(text, label), "label": label, "injection_type": "Dissonant"})

        # Tier 3: Social
        emoji_s = injector.get_social(label)
        if emoji_s:
            augmented_data.append({"text": text, "emoji": emoji_s, "label": label, "injection_type": "Social"})

    # Save
    output_filename = f"train_{'50' if args.mode == 'standard' else '100'}.csv"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    pd.DataFrame(augmented_data).to_csv(output_path, index=False)
    print(f"Saved {args.mode} dataset to {output_path} with {len(augmented_data)} rows.")

if __name__ == "__main__":
    main()
