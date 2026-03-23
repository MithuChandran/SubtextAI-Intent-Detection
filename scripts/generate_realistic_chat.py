import random
from datetime import datetime, timedelta

# Realistic conversations scenarios
conversations = [
    [
        ("Alice", "Hey, did you see the email from HR? 📧"),
        ("Bob", "Yeah, about the new policy? Seems kinda strict. 😕"),
        ("Alice", "I know right! I might actually have to come into the office now 😩"),
        ("Bob", "Haha RIP remote life ☠️"),
        ("Alice", "Don't laugh, it's serious! I sold my car 🚗"),
        ("Bob", "Wait seriously?? 😲"),
        ("Alice", "No lol just kidding 😂"),
        ("Bob", "You almost got me there 😒")
    ],
    [
        ("Charlie", "Anyone up for drinks tonight? 🍻"),
        ("Dave", "I'm down! Where we going?"),
        ("Eve", "I can't, have to finish this project 😫"),
        ("Charlie", "Come on Eve, just for one! 🥺"),
        ("Eve", "Last time 'just one' turned into 3am karaoke 🎤"),
        ("Dave", "That was legendary though 🔥"),
        ("Charlie", "Exactly! You can't miss out 🤷‍♂️"),
        ("Eve", "Fine... but I'm leaving by 10. 🕙"),
        ("Charlie", "Sure you are 😉"),
        ("Dave", "See you guys at the usual spot! 📍")
    ],
    [
        ("Alice", "Happy birthday Bob!! 🎂🎉"),
        ("Charlie", "Happy birthday man! 🎈"),
        ("Bob", "Thanks guys! Appreciate it 🙏"),
        ("Eve", "Happy birthday! Hope you have a great one ✨"),
        ("Bob", "Thanks Eve! We're grabbing dinner later if you wanna come."),
        ("Eve", "I'd love to! What time? ⏰"),
        ("Bob", "Around 8ish at Mario's 🍕"),
        ("Eve", "Perfect, see you then! 👋")
    ],
    [
        ("Dave", "Bro did you watch the game? 🏀"),
        ("Charlie", "Yeah what a finish! 🤯"),
        ("Dave", "That last shot was insane"),
        ("Charlie", "I thought they were gonna lose for sure 😅"),
        ("Dave", "Same here. My heart rate is still up 📈"),
        ("Charlie", "Next game is gonna be tough though."),
        ("Dave", "We got this 💪")
    ],
    [
        ("Eve", "Can someone review my PR? It's urgent 🚨"),
        ("Alice", "I'm in a meeting but I can check in an hour."),
        ("Eve", "Thanks Alice! 🙏"),
        ("Bob", "I can look at it now 👀"),
        ("Eve", "You're a lifesaver Bob! ❤️"),
        ("Bob", "Just left some comments. Mostly nitpicks."),
        ("Eve", "On it! 👩‍💻"),
        ("Bob", "LGTM now 👍"),
        ("Eve", "Merging! 🚀")
    ],
    [
        ("Charlie", "This traffic is a nightmare 🚗🚙🚛"),
        ("Alice", "Where are you?"),
        ("Charlie", "Stuck on the 405. Hasn't moved in 20 mins 🤬"),
        ("Alice", "Oof. You're gonna be late?"),
        ("Charlie", "Yeah start without me 😞"),
        ("Alice", "Okay, drive safe! 🛡️")
    ],
    [
        ("Dave", "Check out this meme lol <image_omitted>"),
        ("Bob", "😂😂😂"),
        ("Charlie", "I feel personally attacked 💀"),
        ("Dave", "It's literally you yesterday"),
        ("Bob", "True story 💯")
    ],
    [
        ("Alice", "Guys I have some bad news..."),
        ("Eve", "What happened?? 😰"),
        ("Alice", "They discontinued the spicy chicken wrap 😭"),
        ("Eve", "Omg you scared me!"),
        ("Alice", "This IS scary! What am I gonna eat for lunch? 🥗"),
        ("Eve", "You're dramatic 🙄"),
        ("Alice", "And you're unsupportive 😤")
    ]
]

def generate_chat(output_file: str, count: int):
    start_time = datetime(2024, 1, 15, 9, 0, 0)
    output_lines = []
    
    # Generate messages by looping through scenarios
    while len(output_lines) < count:
        scenario = random.choice(conversations)
        # Add a time gap between conversations
        start_time += timedelta(minutes=random.randint(30, 120))
        
        for user, msg in scenario:
            # Message gap
            start_time += timedelta(seconds=random.randint(10, 120))
            ts_str = start_time.strftime("%d/%m/%Y, %H:%M")
            output_lines.append(f"{ts_str} - {user}: {msg}\n")
            
            if len(output_lines) >= count:
                break
                
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"Generated {output_file} with {len(output_lines)} realistic messages.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic chat data.")
    parser.add_argument("--output", type=str, default="tests/test_chat_real_100.txt", help="Output file path")
    parser.add_argument("--count", type=int, default=100, help="Number of messages to generate")
    
    args = parser.parse_args()
    generate_chat(args.output, args.count)
