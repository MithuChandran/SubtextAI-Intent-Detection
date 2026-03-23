import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_realistic_chat import generate_chat

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill: Generate Synthetic Chat Data")
    parser.add_argument("--output", type=str, default="data/generated_chat.txt", help="Output file path")
    parser.add_argument("--count", type=int, default=100, help="Number of messages to generate")
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} messages to {args.output}...")
    generate_chat(args.output, args.count)
    print("Done.")
