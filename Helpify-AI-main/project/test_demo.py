#!/usr/bin/env python
"""Quick demo test of trained models"""

import sys
sys.path.insert(0, '.')

from src.data_pipeline import Dataset, TextVectorizer
from src.models.text_cnn import TextCNN
from src.rl.q_learning import QLearningAgent
import torch
from pathlib import Path
import pandas as pd

print("=" * 70)
print("🚀 HELPIFY AI - TRAINED MODEL DEMO")
print("=" * 70)

# Rebuild vectorizer from training data
print("\n📦 Loading trained models...")

# Load training data to rebuild vectorizer
dataset = Dataset()
train_df = pd.read_csv("data/processed/train.csv")
vectorizer = TextVectorizer(vocab_size=5000, max_length=50)
vectorizer.build_vocab(train_df["text"].tolist())
print("✓ Vectorizer built from training data")

# Load CNN model
cnn_model = TextCNN(
    vocab_size=5000,
    embedding_dim=300,
    num_classes=10,
    num_filters=100,
    filter_sizes=[2, 3, 4],
    dropout_rate=0.5
)
cnn_model.load_state_dict(torch.load("weights/text_cnn_best.pt", map_location="cpu", weights_only=True))
cnn_model.eval()
print("✓ Text-CNN model loaded")

# Load RL agent
rl_agent = QLearningAgent(num_states=10)
rl_agent.load("weights/q_learning_agent.json")
print("✓ Q-Learning agent loaded")

# Test queries
test_queries = [
    "I want to cancel my subscription",
    "hello there",
    "what is your return policy",
]

print("\n" + "=" * 70)
print("🧪 TESTING WITH SAMPLE QUERIES")
print("=" * 70)

intent_names = [
    "borrow_money", "cancel_subscription", "report_fraud", 
    "account_blocked", "shopping_assistance", "what_is_butts",
    "airline_baggage_policy", "international_visa", 
    "restaurant_reservation", "schedule_maintenance"
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    
    # Preprocess
    preprocessed = dataset.preprocess(query)
    
    # Encode
    encoded = vectorizer.encode(preprocessed)
    encoded_batch = torch.LongTensor([encoded])
    
    # Predict intent
    with torch.no_grad():
        logits, probs = cnn_model(encoded_batch)
        intent_id = torch.argmax(probs, dim=1).item()
        confidence = probs[0, intent_id].item()
    
    intent_name = intent_names[intent_id]
    
    # Select action
    action_id = rl_agent.select_action(intent_id, training=False)
    actions = ["ask_order_id", "provide_solution", "escalate_human", 
               "give_faq", "ask_clarification", "apologize_and_help"]
    action_name = actions[action_id]
    
    print(f"  ✅ Intent: {intent_name} ({confidence:.1%})")
    print(f"  🤖 Action: {action_name}")

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE - ALL MODELS WORKING!")
print("=" * 70)
