import os
import sys

# Add current directory to sys.path to import src
sys.path.append(os.getcwd())

from src.model.interface import DissonanceClassifier

def test_load():
    model_path = "models/intent30_text_emoji_weighted"
    print(f"Testing loading from: {model_path}")
    try:
        classifier = DissonanceClassifier(model_path)
        classifier.load()
        print("SUCCESS: Model loaded successfully!")
        
        # Test a simple prediction
        text = "I am so happy today!"
        emoji = "😊"
        result = classifier.predict(text, emoji)
        print(f"Prediction result: {result}")
        
    except Exception as e:
        print(f"ERROR: Failed to load model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
