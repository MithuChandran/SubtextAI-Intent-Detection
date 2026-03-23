"""
Architecture Comparison Training Script
Supports multiple approaches: baseline, bertweet, class-weighted, dual-encoder
"""
import os
import sys
import argparse
sys.path.append(os.getcwd())

import torch
import pandas as pd
import numpy as np
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from sklearn.metrics import accuracy_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import Dataset
from src.model.training_utils import (
    DEFAULT_SEED,
    build_label_maps,
    load_training_frame,
    save_metrics,
    split_train_eval_dataframes,
)

# ============ DATASET CLASSES ============

class SimpleDataset(Dataset):
    """Basic dataset for approaches A, B, C"""
    def __init__(self, data_source, tokenizer, max_len=128, label2id=None, text_mode="text_emoji"):
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
        self.text_mode = text_mode
        
        if label2id is None:
            self.labels = sorted(self.data['label'].unique().tolist())
            self.label2id = {l: i for i, l in enumerate(self.labels)}
        else:
            self.label2id = dict(label2id)
            self.labels = [label for label, _ in sorted(self.label2id.items(), key=lambda item: item[1])]

        self.id2label = {i: l for l, i in self.label2id.items()}
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        if self.text_mode == "text_only":
            text = row["text"]
        else:
            text = f"{row['text']} {row['emoji']}".strip()
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.label2id[row['label']], dtype=torch.long)
        }

# ============ WEIGHTED TRAINER ============

class WeightedTrainer(Trainer):
    """Trainer with class weights for imbalanced data"""
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        
        if self.class_weights is not None:
            weight = torch.tensor(self.class_weights, dtype=torch.float).to(logits.device)
            loss_fct = torch.nn.CrossEntropyLoss(weight=weight)
        else:
            loss_fct = torch.nn.CrossEntropyLoss()
            
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# ============ METRICS ============

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {'accuracy': acc, 'f1': f1}

# ============ TRAINING FUNCTIONS ============

def train_approach(
    approach,
    train_path,
    output_dir,
    epochs=3,
    eval_path=None,
    test_path=None,
    eval_ratio=0.1,
    seed=DEFAULT_SEED,
    text_mode="text_emoji",
):
    """Train a single approach and return metrics"""
    
    print(f"\n{'='*50}")
    print(f"Training Approach {approach.upper()}")
    print(f"{'='*50}")
    
    # Select model based on approach
    if approach == 'bertweet':
        model_name = 'vinai/bertweet-base'
    else:
        model_name = 'roberta-base'  # Using base for speed
    
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, normalization=True if approach == 'bertweet' else False)
    
    train_df = load_training_frame(train_path)
    if eval_path:
        eval_df = load_training_frame(eval_path)
    else:
        train_df, eval_df = split_train_eval_dataframes(train_df, eval_ratio=eval_ratio, seed=seed)

    test_df = load_training_frame(test_path) if test_path else None
    labels, label2id, id2label = build_label_maps(train_df, eval_df, test_df)

    train_dataset = SimpleDataset(train_df, tokenizer, label2id=label2id, text_mode=text_mode)
    val_dataset = SimpleDataset(eval_df, tokenizer, label2id=label2id, text_mode=text_mode)
    test_dataset = (
        SimpleDataset(test_df, tokenizer, label2id=label2id, text_mode=text_mode)
        if test_df is not None
        else None
    )

    num_labels = len(labels)
    print(f"Found {num_labels} labels")
    print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    if test_dataset is not None:
        print(f"Test: {len(test_dataset)}")
    
    # Load model
    print(f"Loading model: {model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )
    
    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=50,
        weight_decay=0.01,
        logging_dir=f'{output_dir}/logs',
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_f1",
        greater_is_better=True,
        report_to="none",
        seed=seed,
    )
    
    # Select trainer
    if approach == 'weighted':
        # Compute class weights
        train_labels = train_dataset.data['label'].values
        classes = np.unique(train_labels)
        weights = compute_class_weight('balanced', classes=classes, y=train_labels)
        weight_dict = {c: w for c, w in zip(classes, weights)}
        class_weights = [weight_dict[l] for l in train_dataset.labels]
        print(f"Using class weights (sample): {list(zip(train_dataset.labels[:5], class_weights[:5]))}")
        
        trainer = WeightedTrainer(
            class_weights=class_weights,
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics
        )
    else:
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics
        )
    
    # Train
    print("Starting training...")
    trainer.train()
    
    # Evaluate
    print("Evaluating...")
    metrics = trainer.evaluate()
    
    # Save
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"\nResults for {approach.upper()}:")
    print(f"  Accuracy: {metrics['eval_accuracy']:.4f}")
    print(f"  F1: {metrics['eval_f1']:.4f}")

    all_metrics = {
        "approach": approach,
        "train_path": train_path,
        "eval_path": eval_path or f"grouped_split:{eval_ratio}",
        "test_path": test_path,
        "train_samples": len(train_dataset),
        "eval_samples": len(val_dataset),
        "text_mode": text_mode,
        "eval_metrics": metrics,
    }

    if test_dataset is not None:
        test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
        print(f"  Test Accuracy: {test_metrics['test_accuracy']:.4f}")
        print(f"  Test F1: {test_metrics['test_f1']:.4f}")
        all_metrics["test_metrics"] = test_metrics

    save_metrics(output_dir, all_metrics)
    
    return metrics, all_metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approach", choices=['baseline', 'bertweet', 'weighted'], required=True)
    parser.add_argument("--train_path", default="data/processed/augmented_train.csv")
    parser.add_argument("--eval_path", default=None)
    parser.add_argument("--test_path", default=None)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--eval_ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--text_mode", choices=["text_only", "text_emoji"], default="text_emoji")
    parser.add_argument("--output_dir", default=None)
    args = parser.parse_args()
    
    output_dir = args.output_dir or f"models/arch_{args.approach}_{args.text_mode}"
    metrics, all_metrics = train_approach(
        args.approach,
        args.train_path,
        output_dir,
        args.epochs,
        eval_path=args.eval_path,
        test_path=args.test_path,
        eval_ratio=args.eval_ratio,
        seed=args.seed,
        text_mode=args.text_mode,
    )
    
    print(f"\n{'='*50}")
    print("FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Approach: {args.approach}")
    print(f"Accuracy: {metrics['eval_accuracy']:.4f}")
    print(f"F1 Score: {metrics['eval_f1']:.4f}")
    if "test_metrics" in all_metrics:
        print(f"Test Accuracy: {all_metrics['test_metrics']['test_accuracy']:.4f}")
        print(f"Test F1 Score: {all_metrics['test_metrics']['test_f1']:.4f}")

if __name__ == "__main__":
    main()
