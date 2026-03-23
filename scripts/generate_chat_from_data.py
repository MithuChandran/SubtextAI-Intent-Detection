import pandas as pd
import random
from datetime import datetime, timedelta

# Load the augmented dataset (1K mini version is sufficient/representative)
df = pd.read_csv("data/processed/train_mini.csv")

# Filter for rows that actually have emojis
df = df[df['emoji'].notna() & (df['emoji'] != "")]

# Sample 100 rows
if len(df) > 100:
    samples = df.sample(100)
else:
    samples = df

users = ["User A", "User B", "User C", "User D"]
start_time = datetime(2024, 1, 20, 10, 0, 0)
output_lines = []

for _, row in samples.iterrows():
    # Advance time randomly
    start_time += timedelta(minutes=random.randint(1, 60))
    ts_str = start_time.strftime("%d/%m/%Y, %H:%M")
    
    user = random.choice(users)
    text = row['text']
    emoji = row['emoji']
    
    # Construct message: "Timestamp - User: Text Emoji"
    # This reflects the exact augmentation structure: text + appended emoji
    msg = f"{ts_str} - {user}: {text} {emoji}\n"
    output_lines.append(msg)

output_path = "tests/test_chat_dataset_100.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"Generated {output_path} with {len(output_lines)} messages from train_mini.csv")
