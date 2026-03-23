"""
Dual-Encoder Architecture: RoBERTa + emoji2vec
Separate encoders for text and emoji with fusion layer
"""
import os
import sys
import argparse
sys.path.append(os.getcwd())

import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from transformers import (
    AutoModel,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import Dataset
import re
from src.model.training_utils import (
    DEFAULT_SEED,
    build_label_maps,
    load_training_frame,
    save_metrics,
    split_train_eval_dataframes,
)

# ============ EMOJI EXTRACTION ============

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+", 
    flags=re.UNICODE
)

def extract_emojis(text):
    """Extract all emojis from text"""
    return EMOJI_PATTERN.findall(str(text))

def remove_emojis(text):
    """Remove emojis from text"""
    return EMOJI_PATTERN.sub('', str(text)).strip()

# ============ DUAL ENCODER MODEL ============

class DualEncoderClassifier(nn.Module):
    """
    Dual encoder: RoBERTa for text + learned emoji embeddings
    """
    def __init__(self, text_model_name, num_labels, emoji_vocab_size=2000, emoji_dim=64):
        super().__init__()
        
        # Text encoder
        self.text_encoder = AutoModel.from_pretrained(text_model_name)
        text_hidden_size = self.text_encoder.config.hidden_size
        
        # Emoji encoder (learnable embeddings)
        self.emoji_embedding = nn.Embedding(emoji_vocab_size, emoji_dim, padding_idx=0)
        self.emoji_pool = nn.AdaptiveAvgPool1d(1)
        
        # Fusion layer
        fusion_dim = text_hidden_size + emoji_dim
        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, num_labels)
        )
        
        self.num_labels = num_labels
        
    def forward(self, input_ids, attention_mask, emoji_ids, labels=None):
        # Encode text
        text_outputs = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask)
        text_pooled = text_outputs.last_hidden_state[:, 0, :]  # CLS token
        
        # Encode emojis
        emoji_embeds = self.emoji_embedding(emoji_ids)  # (batch, seq, dim)
        emoji_pooled = emoji_embeds.mean(dim=1)  # Average pooling
        
        # Fuse
        fused = torch.cat([text_pooled, emoji_pooled], dim=-1)
        
        # Classify
        logits = self.classifier(fused)
        
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits, labels)
            
        return {"loss": loss, "logits": logits}

# ============ DATASET ============

class DualEncoderDataset(Dataset):
    def __init__(self, data_source, tokenizer, max_len=128, max_emoji_len=10, label2id=None):
        if isinstance(data_source, pd.DataFrame):
            self.data = data_source.copy().reset_index(drop=True)
        else:
            self.data = pd.read_csv(data_source)

        if "text" not in self.data.columns:
            self.data["text"] = ""
        if "emoji" not in self.data.columns:
            self.data["emoji"] = ""
        if "label" not in self.data.columns:
            self.data["label"] = ""

        self.data["text"] = self.data["text"].fillna("").astype(str)
        self.data["emoji"] = self.data["emoji"].fillna("").astype(str)
        self.data["label"] = self.data["label"].fillna("").astype(str)
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.max_emoji_len = max_emoji_len
        
        if label2id is None:
            self.labels = sorted(self.data['label'].unique().tolist())
            self.label2id = {l: i for i, l in enumerate(self.labels)}
        else:
            self.label2id = dict(label2id)
            self.labels = [label for label, _ in sorted(self.label2id.items(), key=lambda item: item[1])]

        self.id2label = {i: l for l, i in self.label2id.items()}
        
        # Build emoji vocabulary from data
        all_emojis = set()
        for text in self.data['text'].tolist() + self.data['emoji'].tolist():
            all_emojis.update(extract_emojis(str(text)))
        self.emoji2id = {e: i+1 for i, e in enumerate(sorted(all_emojis))}  # 0 is padding
        self.emoji2id['<PAD>'] = 0
        
        print(f"Built emoji vocab with {len(self.emoji2id)} unique emojis")
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        
        # Separate text and emojis
        full_text = f"{row['text']} {row['emoji']}"
        clean_text = remove_emojis(full_text)
        emojis = extract_emojis(full_text)
        
        # Tokenize text
        encoding = self.tokenizer(
            clean_text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Encode emojis
        emoji_ids = [self.emoji2id.get(e, 0) for e in emojis[:self.max_emoji_len]]
        emoji_ids = emoji_ids + [0] * (self.max_emoji_len - len(emoji_ids))  # Pad
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'emoji_ids': torch.tensor(emoji_ids, dtype=torch.long),
            'labels': torch.tensor(self.label2id[row['label']], dtype=torch.long)
        }

# ============ METRICS ============

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {'accuracy': acc, 'f1': f1}

# ============ CUSTOM TRAINER ============

class DualEncoderTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        emoji_ids = inputs.pop("emoji_ids")
        
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            emoji_ids=emoji_ids,
            labels=labels
        )
        
        loss = outputs["loss"]
        return (loss, outputs) if return_outputs else loss

# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", default="data/processed/augmented_train.csv")
    parser.add_argument("--eval_path", default=None)
    parser.add_argument("--test_path", default=None)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--eval_ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    
    print("="*50)
    print("Training DUAL-ENCODER (RoBERTa + Emoji Embeddings)")
    print("="*50)
    
    model_name = "roberta-base"
    output_dir = "models/arch_dual_encoder_full"
    
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    train_df = load_training_frame(args.train_path)
    if args.eval_path:
        eval_df = load_training_frame(args.eval_path)
    else:
        train_df, eval_df = split_train_eval_dataframes(
            train_df,
            eval_ratio=args.eval_ratio,
            seed=args.seed,
        )

    test_df = load_training_frame(args.test_path) if args.test_path else None
    labels, label2id, _ = build_label_maps(train_df, eval_df, test_df)

    train_dataset = DualEncoderDataset(train_df, tokenizer, label2id=label2id)
    val_dataset = DualEncoderDataset(eval_df, tokenizer, label2id=label2id)
    test_dataset = DualEncoderDataset(test_df, tokenizer, label2id=label2id) if test_df is not None else None

    num_labels = len(labels)
    emoji_vocab_size = len(train_dataset.emoji2id)
    print(f"Found {num_labels} labels, {emoji_vocab_size} emoji types")
    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    if test_dataset is not None:
        print(f"Test: {len(test_dataset)}")
    
    # Create model
    print("Creating Dual-Encoder model...")
    model = DualEncoderClassifier(
        text_model_name=model_name,
        num_labels=num_labels,
        emoji_vocab_size=emoji_vocab_size,
        emoji_dim=64
    )
    
    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir=f'{output_dir}/logs',
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
        seed=args.seed,
    )
    
    trainer = DualEncoderTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Evaluating...")
    metrics = trainer.evaluate()
    
    # Save
    torch.save(model.state_dict(), f"{output_dir}/model.pt")
    tokenizer.save_pretrained(output_dir)
    
    print(f"\nResults for DUAL-ENCODER:")
    print(f"  Accuracy: {metrics['eval_accuracy']:.4f}")
    print(f"  F1: {metrics['eval_f1']:.4f}")

    all_metrics = {
        "approach": "dual-encoder",
        "train_path": args.train_path,
        "eval_path": args.eval_path or f"grouped_split:{args.eval_ratio}",
        "test_path": args.test_path,
        "train_samples": len(train_dataset),
        "eval_samples": len(val_dataset),
        "eval_metrics": metrics,
    }

    if test_dataset is not None:
        test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
        print(f"  Test Accuracy: {test_metrics['test_accuracy']:.4f}")
        print(f"  Test F1: {test_metrics['test_f1']:.4f}")
        all_metrics["test_metrics"] = test_metrics

    save_metrics(output_dir, all_metrics)
    
    print(f"\n{'='*50}")
    print("FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Approach: dual-encoder")
    print(f"Accuracy: {metrics['eval_accuracy']:.4f}")
    print(f"F1 Score: {metrics['eval_f1']:.4f}")
    if "test_metrics" in all_metrics:
        print(f"Test Accuracy: {all_metrics['test_metrics']['test_accuracy']:.4f}")
        print(f"Test F1 Score: {all_metrics['test_metrics']['test_f1']:.4f}")

if __name__ == "__main__":
    main()
