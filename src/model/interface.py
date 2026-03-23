import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


HIGH_DISSONANCE_LABELS = {
    "Complain",
    "Criticize",
    "Oppose",
    "Taunt",
}

MEDIUM_DISSONANCE_LABELS = {
    "Doubt",
    "Flaunt",
    "Prevent",
    "Warn",
}

DIRECT_DISSONANCE_LEVELS = {"Low", "Medium", "High"}
DIRECT_DISSONANCE_VALUES = {
    "Low": 0.0,
    "Medium": 0.5,
    "High": 1.0,
}


def _derive_dissonance(label_probs):
    high_prob = sum(label_probs.get(label, 0.0) for label in HIGH_DISSONANCE_LABELS)
    medium_prob = sum(label_probs.get(label, 0.0) for label in MEDIUM_DISSONANCE_LABELS)
    score = min(1.0, high_prob + (0.5 * medium_prob))

    if score >= 0.67:
        level = "High"
    elif score >= 0.34:
        level = "Medium"
    else:
        level = "Low"

    return score, level


class SequenceLabelClassifier:
    def __init__(self, model_path):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def load(self):
        try:
            print(f"Loading model from {self.model_path}...")
            # Try loading tokenizer (with a fallback for slow tokenizers)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            except ValueError:
                print("Fast tokenizer failed. Attempting to load slow tokenizer...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=False)
            
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            print("Model loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {self.model_path}: {e}") from e

    def predict(self, text, emoji):
        return self.predict_batch([text], [emoji])[0]

    def predict_batch(self, texts, emojis):
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model is not loaded.")

        input_texts = [f"{t} {e}" for t, e in zip(texts, emojis)]
        inputs = self.tokenizer(
            input_texts, 
            return_tensors="pt", 
            truncation=True, 
            max_length=128,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            all_probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            all_top_probs, all_top_classes = torch.max(all_probs, dim=-1)

        results = []
        for i in range(len(texts)):
            probs = all_probs[i]
            top_prob = float(all_top_probs[i].item())
            top_class = int(all_top_classes[i].item())
            
            label_probs = {
                self.model.config.id2label[idx]: float(probs[idx].item())
                for idx in range(probs.shape[-1])
            }
            dialogue_act = self.model.config.id2label[top_class]

            results.append({
                "label": dialogue_act,
                "confidence": top_prob,
                "label_probs": label_probs,
            })
        return results


class DissonanceClassifier(SequenceLabelClassifier):
    def predict(self, text, emoji):
        return self.predict_batch([text], [emoji])[0]

    def predict_batch(self, texts, emojis):
        base_predictions = super().predict_batch(texts, emojis)
        results = []
        
        for prediction in base_predictions:
            label_probs = prediction["label_probs"]
            top_label = prediction["label"]

            if set(label_probs.keys()).issubset(DIRECT_DISSONANCE_LEVELS):
                dissonance_score = sum(
                    DIRECT_DISSONANCE_VALUES[level] * probability
                    for level, probability in label_probs.items()
                )
                dissonance_level = top_label
                dialogue_act = None
                dialogue_act_confidence = None
            else:
                dissonance_score, dissonance_level = _derive_dissonance(label_probs)
                dialogue_act = top_label
                dialogue_act_confidence = prediction["confidence"]

            results.append({
                "dissonance_score": dissonance_score,
                "label": dissonance_level,
                "dissonance_level": dissonance_level,
                "dialogue_act": dialogue_act,
                "dialogue_act_confidence": dialogue_act_confidence,
            })
        return results


class IntentClassifier(SequenceLabelClassifier):
    def predict(self, text, emoji):
        prediction = super().predict(text, emoji)
        return {
            "intent": prediction["label"],
            "intent_confidence": prediction["confidence"],
        }
