import torch
from torch.utils.data import Dataset
import pandas as pd
from transformers import AutoTokenizer

class DissonanceDataset(Dataset):
    def __init__(
        self,
        data_source,
        tokenizer_name="roberta-large",
        tokenizer=None,
        max_len=128,
        label2id=None,
    ):
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

        self.tokenizer = tokenizer or AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_len = max_len
        
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
        text = str(row['text'])
        emoji = "" if pd.isna(row['emoji']) else str(row['emoji'])
        label = row['label']
        
        # Combine Text + Emoji
        # Strategy: "Text [SEP] Emoji" or just concatenation
        combined_text = f"{text} {emoji}"
        
        encoding = self.tokenizer.encode_plus(
            combined_text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.label2id[label], dtype=torch.long)
        }
