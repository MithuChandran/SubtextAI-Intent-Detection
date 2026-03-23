import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser.whatsapp_parser import WhatsAppParser
from src.model.interface import DissonanceClassifier, IntentClassifier

DEFAULT_DISSONANCE_MODEL_CANDIDATES = (
    "models/dissonance3_text_emoji_weighted",
    "models/dissonance3_text_only_weighted",
    "models/arch_weighted_full",
    "models/arch_weighted",
)

DEFAULT_INTENT_MODEL_CANDIDATES = (
    "models/intent30_text_emoji_baseline",
    "models/intent30_text_only_baseline",
    "models/arch_weighted_full",
    "models/arch_weighted",
)


def resolve_default_model_path(candidates):
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[-1]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill: Analyze Chat Log for Dissonance")
    parser.add_argument("--file", type=str, required=True, help="Path to chat log file (.txt)")
    parser.add_argument(
        "--dissonance-model",
        type=str,
        default=resolve_default_model_path(DEFAULT_DISSONANCE_MODEL_CANDIDATES),
        help="Path to 3-class dissonance model directory",
    )
    parser.add_argument(
        "--intent-model",
        type=str,
        default=resolve_default_model_path(DEFAULT_INTENT_MODEL_CANDIDATES),
        help="Path to intent model directory",
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        sys.exit(1)

    print(f"Loading dissonance model from {args.dissonance_model}...")
    try:
        dissonance_classifier = DissonanceClassifier(args.dissonance_model)
        dissonance_classifier.load()
        print(f"Loading intent model from {args.intent_model}...")
        intent_classifier = IntentClassifier(args.intent_model)
        intent_classifier.load()
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback or exit? For a skill, let's exit.
        sys.exit(1)

    print("Parsing chat log...")
    parser = WhatsAppParser()
    try:
        df = parser.parse_file(args.file)
        print(f"Parsed {len(df)} messages.")
    except Exception as e:
        print(f"Error parsing file: {e}")
        sys.exit(1)

    print("Analyzing for dissonance...")
    results = []
    for _, row in df.iterrows():
        dissonance_prediction = dissonance_classifier.predict(row['message'], "")
        intent_prediction = intent_classifier.predict(row['message'], "")
        results.append({
            "timestamp": row['timestamp'],
            "sender": row['sender'],
            "message": row['message'],
            "dissonance_score": dissonance_prediction['dissonance_score'],
            "label": dissonance_prediction['label'],
            "dissonance_level": dissonance_prediction['dissonance_level'],
            "dialogue_act": intent_prediction['intent'],
            "dialogue_act_confidence": intent_prediction['intent_confidence'],
        })
    
    # Identify high dissonance messages
    high_dissonance = [r for r in results if r['dissonance_level'] == 'High']
    
    print("\n--- Analysis Results ---")
    print(f"Total Messages: {len(results)}")
    print(f"Dissonant Messages: {len(high_dissonance)}")
    
    if high_dissonance:
        print("\nTop Dissonant Messages:")
        # Sort by score desc
        high_dissonance.sort(key=lambda x: x['dissonance_score'], reverse=True)
        for msg in high_dissonance[:5]:
            print(
                f"[{msg['timestamp']}] {msg['sender']}: {msg['message']} "
                f"(Level: {msg['dissonance_level']}, Act: {msg['dialogue_act']}, Score: {msg['dissonance_score']:.2f})"
            )
    
    # Save results
    output_csv = args.file + ".analysis.csv"
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"\nFull results saved to {output_csv}")
