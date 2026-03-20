# Baseline ML + DL models
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import torch.optim as optim

# -------------------------------
# Step 1: Load dataset
# -------------------------------
df_train = pd.read_csv("data/processed/train.csv")
df_val = pd.read_csv("data/processed/val.csv")

# Use 'text' as input and 'inbound' as target
X_train = df_train['text'].values
y_train = df_train['inbound'].astype(int).values  # convert bool to int
X_val = df_val['text'].values
y_val = df_val['inbound'].astype(int).values

# -------------------------------
# Step 2: Check class balance
# -------------------------------
print("=== Class Balance - Train ===")
print(df_train['inbound'].value_counts())
print("\n=== Class Balance - Validation ===")
print(df_val['inbound'].value_counts())

# -------------------------------
# Step 3: ML Baselines
# -------------------------------
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_val_vec = vectorizer.transform(X_val)

# Logistic Regression
lr_model = LogisticRegression()
lr_model.fit(X_train_vec, y_train)
y_pred_lr = lr_model.predict(X_val_vec)
print("\n=== Logistic Regression ===")
print(classification_report(y_val, y_pred_lr, zero_division=0))

# Decision Tree
dt_model = DecisionTreeClassifier()
dt_model.fit(X_train_vec, y_train)
y_pred_dt = dt_model.predict(X_val_vec)
print("\n=== Decision Tree ===")
print(classification_report(y_val, y_pred_dt, zero_division=0))

# -------------------------------
# Step 4: Show sample predictions
# -------------------------------
print("\n=== Sample Predictions (Logistic Regression) ===")
for text, pred in zip(X_val[:5], y_pred_lr[:5]):
    print(f"Tweet: {text[:50]}... | Predicted inbound: {pred}")

# -------------------------------
# Step 5: DL Baseline (Feedforward)
# -------------------------------
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

class FeedForwardNN(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))

input_dim = X_train_vec.shape[1]
model = FeedForwardNN(input_dim)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(5):
    model.train()
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} finished")

# Evaluate on validation
model.eval()
all_preds = []
all_labels = []
with torch.no_grad():
    for X_batch, y_batch in val_loader:
        outputs = model(X_batch)
        preds = torch.argmax(outputs, dim=1)
        all_preds.extend(preds.tolist())
        all_labels.extend(y_batch.tolist())

print("\n=== Feedforward NN ===")
print(classification_report(all_labels, all_preds, zero_division=0))

# Sample DL predictions
print("\n=== Sample Predictions (Feedforward NN) ===")
for text, pred in zip(X_val[:5], all_preds[:5]):
    print(f"Tweet: {text[:50]}... | Predicted inbound: {pred}")