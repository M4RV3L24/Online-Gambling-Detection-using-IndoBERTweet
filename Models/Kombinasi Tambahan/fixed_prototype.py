# TF-IDF + BiLSTM Hybrid Model

import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from collections import Counter
import re

# Load data
with open('/kaggle/input/fetched-data-final-2/fetched_data_final_dedup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.DataFrame(data)
df['label'] = df['label'].astype(int)

X = df['text']
y = df['label']

# Simple tokenization
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# Build vocabulary
all_tokens = []
for text in X:
    all_tokens.extend(tokenize(text))

vocab = Counter(all_tokens)
vocab = {word: i+2 for i, (word, _) in enumerate(vocab.most_common(10000))}
vocab['<PAD>'] = 0
vocab['<UNK>'] = 1

# Convert texts to sequences
def text_to_sequence(text, vocab, max_len=100):
    tokens = tokenize(text)
    seq = [vocab.get(token, vocab['<UNK>']) for token in tokens]
    return seq[:max_len]

sequences = [text_to_sequence(text, vocab) for text in X]

# TF-IDF features
tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
X_tfidf = tfidf.fit_transform(X).toarray()
scaler = StandardScaler()
X_tfidf = scaler.fit_transform(X_tfidf)

# Split data
X_seq_train, X_seq_val, X_tfidf_train, X_tfidf_val, y_train, y_val = train_test_split(
    sequences, X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

class HybridDataset(torch.utils.data.Dataset):
    def __init__(self, sequences, tfidf_features, labels):
        self.sequences = sequences
        self.tfidf_features = tfidf_features
        self.labels = labels
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return (
            torch.tensor(self.sequences[idx], dtype=torch.long),
            torch.tensor(self.tfidf_features[idx], dtype=torch.float32),
            torch.tensor(self.labels.iloc[idx], dtype=torch.float32)
        )

def collate_fn(batch):
    sequences, tfidf_features, labels = zip(*batch)
    sequences = pad_sequence(sequences, batch_first=True, padding_value=0)
    tfidf_features = torch.stack(tfidf_features)
    labels = torch.stack(labels)
    return sequences, tfidf_features, labels

class HybridTfidfBiLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=100, hidden_dim=64, tfidf_dim=1000):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        
        # Combine LSTM output with TF-IDF features
        self.fc = nn.Linear(hidden_dim * 2 + tfidf_dim, 64)
        self.classifier = nn.Linear(64, 1)
        
    def forward(self, sequences, tfidf_features):
        # LSTM branch
        embedded = self.embedding(sequences)
        lstm_out, (h_n, _) = self.lstm(embedded)
        # Use last hidden states
        lstm_features = torch.cat((h_n[-2], h_n[-1]), dim=1)
        lstm_features = self.dropout(lstm_features)
        
        # Combine with TF-IDF
        combined = torch.cat([lstm_features, tfidf_features], dim=1)
        x = torch.relu(self.fc(combined))
        x = self.dropout(x)
        return torch.sigmoid(self.classifier(x))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_dataset = HybridDataset(X_seq_train, X_tfidf_train, y_train)
val_dataset = HybridDataset(X_seq_val, X_tfidf_val, y_val)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_dataset, batch_size=32, collate_fn=collate_fn)

model = HybridTfidfBiLSTM(len(vocab)).to(device)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

epochs = 20
for epoch in range(epochs):
    model.train()
    train_loss = 0
    
    for sequences, tfidf_features, labels in train_loader:
        sequences = sequences.to(device)
        tfidf_features = tfidf_features.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        preds = model(sequences, tfidf_features).squeeze()
        loss = criterion(preds, labels)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
    
    # Validation
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for sequences, tfidf_features, labels in val_loader:
            sequences = sequences.to(device)
            tfidf_features = tfidf_features.to(device)
            preds = model(sequences, tfidf_features).squeeze().cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())
    
    all_preds = (np.array(all_preds) > 0.5).astype(int)
    
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    
    print(f"Epoch [{epoch+1}/{epochs}] | "
          f"Loss: {train_loss:.4f} | "
          f"Acc: {acc:.4f} | Prec: {prec:.4f} | "
          f"Rec: {rec:.4f} | F1: {f1:.4f}")