import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

# Load datasets
df_train = pd.read_csv("data/processed/train.csv")
df_val = pd.read_csv("data/processed/val.csv")

# Convert 'inbound' to int
y_train = df_train['inbound'].astype(int).values
y_val = df_val['inbound'].astype(int).values
X_train = df_train['text'].values
X_val = df_val['text'].values

# Vectorizer for vocabulary
vectorizer = CountVectorizer(max_features=5000)
vectorizer.fit(X_train)
vocab = vectorizer.vocabulary_

# Dataset class
class TextDataset(Dataset):
    def __init__(self, X, y, vectorizer):
        self.X = vectorizer.transform(X).toarray()
        self.y = y
    def __len__(self):
        return len(self.y)
    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.long)

train_dataset = TextDataset(X_train, y_train, vectorizer)
val_dataset = TextDataset(X_val, y_val, vectorizer)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=8)

# Text-CNN Model
class TextCNN(nn.Module):
    def __init__(self, input_dim, hidden_dim=50, output_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = TextCNN(input_dim=len(vocab))
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop (small baseline)
for epoch in range(5):
    model.train()
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} finished")

# Evaluate
model.eval()
all_preds = []
all_labels = []
with torch.no_grad():
    for X_batch, y_batch in val_loader:
        outputs = model(X_batch)
        preds = torch.argmax(outputs, dim=1)
        all_preds.extend(preds.tolist())
        all_labels.extend(y_batch.tolist())

from sklearn.metrics import classification_report
print("\n=== Text-CNN ===")
print(classification_report(all_labels, all_preds, zero_division=0))