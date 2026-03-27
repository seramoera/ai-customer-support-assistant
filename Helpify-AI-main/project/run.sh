#!/bin/bash

# Helpify AI - Complete ML Research Project
# One-command reproducibility script
# Run: bash run.sh

set -e  # Exit on error

echo "=================================================="
echo "🤖 Helpify AI - Complete ML Pipeline"
echo "=================================================="
echo ""

# 1. Setup Environment
echo "📦 Step 1: Setting up environment..."
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate  # Windows Git Bash
else
    source venv/bin/activate  # Linux/Mac
fi

echo "  Installing dependencies..."
pip install -r requirements.txt -q

echo "✓ Environment ready"
echo ""

# 2. Data Preprocessing
echo "🔄 Step 2: Data preparation and preprocessing..."
cd src
python -c "
from data_pipeline import Dataset, TextVectorizer
import json

# Create sample dataset
print('  Creating sample dataset (Banking77-inspired)...')
dataset = Dataset()
pipeline = dataset.prepare_pipeline()

print(f'  ✓ Dataset: {len(pipeline[\"train\"])} train, {len(pipeline[\"val\"])} val, {len(pipeline[\"test\"])} test')
print(f'  ✓ Intents: {len(dataset.INTENTS)}')
print(f'  ✓ Vocabulary size: {pipeline[\"vectorizer\"].vocab_size}')
"
cd ..

echo "✓ Data ready"
echo ""

# 3. Train Text-CNN Model
echo "🧠 Step 3: Training Text-CNN deep learning model..."
cd src
python -c "
import torch
from data_pipeline import Dataset, TextVectorizer
from models.text_cnn import TextCNN, TrainingUtils
from pathlib import Path
import json

print('  Loading data...')
dataset = Dataset()
pipeline = dataset.prepare_pipeline()
train_data = pipeline['train']
val_data = pipeline['val']
test_data = pipeline['test']
vectorizer = pipeline['vectorizer']

print('  Initializing Text-CNN model...')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = TextCNN(vocab_size=vectorizer.vocab_size, num_classes=8).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

print('  Training...')
best_val_acc = 0
patience = 5
patience_counter = 0

for epoch in range(10):  # Reduced for demo, use 30 in real runs
    train_loss = TrainingUtils.train_epoch(model, train_data, optimizer, criterion, device, batch_size=32)
    val_metrics = TrainingUtils.evaluate(model, val_data, device, batch_size=32)
    
    if val_metrics['accuracy'] > best_val_acc:
        best_val_acc = val_metrics['accuracy']
        Path('../../weights').mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), '../../weights/text_cnn_best.pt')
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f'  Early stopping at epoch {epoch+1}')
            break
    
    print(f'    Epoch {epoch+1}: train_loss={train_loss:.4f}, val_acc={val_metrics[\"accuracy\"]:.1%}')

test_metrics = TrainingUtils.evaluate(model, test_data, device, batch_size=32)
print(f'  ✓ Text-CNN trained: Test Acc={test_metrics[\"accuracy\"]:.1%}, F1={test_metrics[\"f1_macro\"]:.1%}')

import pickle
with open('../../weights/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
"
cd ..

echo "✓ Text-CNN model trained"
echo ""

# 4. Train RL Agent
echo "🎮 Step 4: Training Q-Learning RL agent..."
cd src
python -c "
from rl.q_learning import QLearningAgent
import json

print('  Initializing Q-Learning agent...')
agent = QLearningAgent(num_states=8, learning_rate=0.1, discount_factor=0.9)

print('  Training on 500 episodes...')
agent.train(episodes=500)

stats = agent.get_statistics()
print(f'  ✓ Q-Learning trained:')
print(f'    - Total reward: {stats[\"total_reward\"]:.1f}')
print(f'    - Success rate: {stats[\"success_rate\"]:.1%}')
print(f'    - Avg episode reward: {stats[\"avg_reward\"]:.2f}')

import json
from pathlib import Path
Path('../../weights').mkdir(parents=True, exist_ok=True)

agent.save('../../weights/q_learning_agent.json')
with open('../../experiments/results/rl_statistics.json', 'w') as f:
    json.dump(stats, f, indent=2)
"
cd ..

echo "✓ Q-Learning agent trained"
echo ""

# 5. Evaluation
echo "📊 Step 5: Comprehensive evaluation..."
cd src
python -c "
import torch
import json
from pathlib import Path
from data_pipeline import Dataset
import pickle

device = 'cuda' if torch.cuda.is_available() else 'cpu'

print('  Loading models...')
dataset = Dataset()
pipeline = dataset.prepare_pipeline()
test_data = pipeline['test']

with open('../../weights/vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

from models.text_cnn import TextCNN, TrainingUtils
model = TextCNN(vocab_size=vectorizer.vocab_size, num_classes=8).to(device)
model.load_state_dict(torch.load('../../weights/text_cnn_best.pt', map_location=device))
model.eval()

print('  Computing metrics...')
metrics = TrainingUtils.evaluate(model, test_data, device, batch_size=32)

# Save evaluation results
Path('../../experiments/results').mkdir(parents=True, exist_ok=True)
with open('../../experiments/results/evaluation_metrics.json', 'w') as f:
    json.dump({
        'accuracy': float(metrics['accuracy']),
        'f1_macro': float(metrics['f1_macro']),
        'f1_weighted': float(metrics['f1_weighted']),
        'precision': float(metrics.get('precision', 0)),
        'recall': float(metrics.get('recall', 0)),
        'model': 'Text-CNN',
        'test_samples': len(test_data)
    }, f, indent=2)

print(f'  ✓ Evaluation complete:')
print(f'    - Accuracy: {metrics[\"accuracy\"]:.1%}')
print(f'    - Macro F1: {metrics[\"f1_macro\"]:.1%}')
print(f'    - Weighted F1: {metrics[\"f1_weighted\"]:.1%}')
"
cd ..

echo "✓ Evaluation complete"
echo ""

# 6. Results Summary
echo "=================================================="
echo "✅ PIPELINE COMPLETE!"
echo "=================================================="
echo ""
echo "📁 Output Files:"
echo "  • weights/text_cnn_best.pt - Trained CNN model"
echo "  • weights/q_learning_agent.json - Trained RL agent"
echo "  • weights/vectorizer.pkl - Text vectorizer"
echo "  • experiments/results/evaluation_metrics.json - Test metrics"
echo "  • experiments/results/rl_statistics.json - RL training stats"
echo ""
echo "🚀 Run Demo:"
echo "  cd src"
echo "  python demo.py"
echo ""
echo "📓 View Configuration:"
echo "  experiments/configs/text_cnn.yaml"
echo "  experiments/configs/rl_agent.yaml"
echo ""
echo "==========================================="
