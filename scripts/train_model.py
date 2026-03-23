import os
import sys
import argparse
sys.path.append(os.getcwd())
import torch
import pandas as pd
from transformers import (
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments,
    AutoTokenizer
)
from src.model.dataset import DissonanceDataset
from src.model.training_utils import (
    DEFAULT_SEED,
    build_label_maps,
    load_training_frame,
    save_metrics,
    split_train_eval_dataframes,
)
from sklearn.metrics import accuracy_score, f1_score

# Config defaults
DEFAULT_TRAIN_PATH = "data/processed/augmented_train.csv"
DEFAULT_MODEL_NAME = "roberta-base"
DEFAULT_OUTPUT_DIR = "models/dissonance_classifier_full"

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {'accuracy': acc, 'f1': f1}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", default=DEFAULT_TRAIN_PATH, help="Path to training CSV")
    parser.add_argument("--eval_path", default=None, help="Optional path to evaluation CSV")
    parser.add_argument("--test_path", default=None, help="Optional path to test CSV")
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR, help="Directory to save model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--eval_ratio", type=float, default=0.1, help="Grouped validation ratio when eval_path is not supplied")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed")
    args = parser.parse_args()

    if not os.path.exists(args.train_path):
        print(f"Dataset not found at {args.train_path}. Please provide the data.")
        return

    print(f"Loading training dataset from {args.train_path}")
    train_df = load_training_frame(args.train_path)
    if args.eval_path:
        print(f"Loading evaluation dataset from {args.eval_path}")
        eval_df = load_training_frame(args.eval_path)
    else:
        print("Creating leakage-safe grouped train/eval split from the full dataset...")
        train_df, eval_df = split_train_eval_dataframes(
            train_df,
            eval_ratio=args.eval_ratio,
            seed=args.seed,
        )

    test_df = load_training_frame(args.test_path) if args.test_path else None
    labels, label2id, id2label = build_label_maps(train_df, eval_df, test_df)
    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_NAME)

    train_dataset = DissonanceDataset(
        train_df,
        tokenizer_name=DEFAULT_MODEL_NAME,
        tokenizer=tokenizer,
        label2id=label2id,
    )
    val_dataset = DissonanceDataset(
        eval_df,
        tokenizer_name=DEFAULT_MODEL_NAME,
        tokenizer=tokenizer,
        label2id=label2id,
    )
    test_dataset = (
        DissonanceDataset(
            test_df,
            tokenizer_name=DEFAULT_MODEL_NAME,
            tokenizer=tokenizer,
            label2id=label2id,
        )
        if test_df is not None
        else None
    )

    num_labels = len(labels)
    print(f"Found {num_labels} labels: {labels}")
    print(f"Training on {len(train_dataset)} samples, validating on {len(val_dataset)} samples.")
    if test_dataset is not None:
        print(f"Test set size: {len(test_dataset)}")

    print("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        DEFAULT_MODEL_NAME, 
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )
    
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=f'{args.output_dir}/logs',
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        no_cuda=not torch.cuda.is_available(),
        report_to="none",
        seed=args.seed,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    print(f"Starting training for {args.output_dir}...")
    trainer.train()
    
    print("Saving model...")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Model saved to {args.output_dir}")

    # Evaluate final
    print("Final Evaluation:")
    eval_metrics = trainer.evaluate()
    print(eval_metrics)

    metrics = {
        "train_path": args.train_path,
        "eval_path": args.eval_path or f"grouped_split:{args.eval_ratio}",
        "test_path": args.test_path,
        "train_samples": len(train_dataset),
        "eval_samples": len(val_dataset),
        "labels": labels,
        "eval_metrics": eval_metrics,
    }

    if test_dataset is not None:
        print("Held-out Test Evaluation:")
        test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")
        print(test_metrics)
        metrics["test_metrics"] = test_metrics

    save_metrics(args.output_dir, metrics)

if __name__ == "__main__":
    main()
