import random
from datetime import datetime, timedelta

users = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
templates = [
    ("Hey everyone! {}", ["👋", "✨", "🌟"]),
    ("Did you see the latest update? {}", ["👀", "🤔", "😮"]),
    ("I'm so tired today... {}", ["😴", "😫", "💤"]),
    ("Great job on the presentation!", ["👏", "🎉", "🔥"]),
    ("Can we reschedule the meeting?", ["📅", "❓", "😬"]),
    ("This code is a mess.", ["😵", "🗑️", "🤦‍♂️"]),
    ("I love this song! {}", ["🎵", "💃", "🎧"]),
    ("Anyone up for lunch?", ["🍔", "🍕", "🥗"]),
    ("Happy birthday!! {}", ["🎂", "🎁", "🎈"]),
    ("I don't agree with that.", ["👎", "🙅‍♀️", "😠"]),
    ("Seriously?", ["😒", "🙄", "🤨"]),
    ("LOL that's so funny", ["😂", "🤣", "💀"]),
    ("I'm feeling much better now.", ["😌", "😊", "❤️"]),
    ("What a beautiful day!", ["☀️", "🌸", "🌈"]),
    ("I'm stuck in traffic.", ["🚗", "🚦", "😫"]),
    ("Check this out: http://example.com", ["🔗", "💻", "👀"]),
    ("No way!", ["😲", "🤯", "😱"]),
    ("Thanks for your help.", ["🙏", "👍", "🤝"]),
    ("I am so angry right now!", ["😡", "🤬", "😤"]),
    ("Let's calming down.", ["🕊️", "🧘", "💆"]),
]

start_time = datetime(2024, 1, 12, 9, 0, 0)

with open("tests/test_chat_100.txt", "w", encoding="utf-8") as f:
    for i in range(100):
        ts = start_time + timedelta(minutes=random.randint(1, 400))
        ts_str = ts.strftime("%d/%m/%Y, %H:%M")
        user = random.choice(users)
        template, emojis = random.choice(templates)
        
        # Randomly decide to add emoji, plain text, or both
        mode = random.choice(["mixed", "mixed", "plain", "emoji_only"])
        
        if mode == "plain":
            # Strip potential brace placeholders if any (though my templates are simple)
            msg = template.format("")
        elif mode == "emoji_only":
             msg = random.choice(emojis)
        else:
             msg = template.format(random.choice(emojis))
             
        line = f"{ts_str} - {user}: {msg}\n"
        f.write(line)

print("Generated tests/test_chat_100.txt with 100 messages.")
