"""
Training Script for Text-CNN + Q-Learning System
"""

import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import logging
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset
import yaml

from data_pipeline import Dataset, TextVectorizer
from models.text_cnn import TextCNN, TrainingUtils
from rl.q_learning import QLearningAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path: str, config_type: str = "text_cnn") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)
    
    if config_type == "text_cnn":
        # Flatten nested config for Text-CNN
        config = {
            # Model config
            "embedding_dim": raw_config["model"]["embedding_dim"],
            "num_filters": raw_config["model"]["num_filters"],
            "filter_sizes": raw_config["model"]["filter_sizes"],
            "dropout_rate": raw_config["model"]["dropout"],
            "num_classes": raw_config["model"]["num_classes"],
            
            # Training config
            "batch_size": raw_config["training"]["batch_size"],
            "learning_rate": raw_config["training"]["learning_rate"],
            "epochs": raw_config["training"]["epochs"],
            "early_stopping_patience": raw_config["training"]["early_stopping_patience"],
            "weight_decay": raw_config["training"]["weight_decay"],
            
            # Data config
            "max_seq_length": raw_config["data"]["max_seq_length"],
            "vocab_size": raw_config["data"]["vocab_size"],
        }
    else:  # RL config
        config = {
            "num_states": raw_config["agent"]["num_states"],
            "num_actions": raw_config["agent"]["num_actions"],
            "learning_rate": raw_config["learning"]["learning_rate"],
            "discount_factor": raw_config["learning"]["discount_factor"],
            "exploration_rate": raw_config["learning"]["exploration_rate"],
            "exploration_decay": raw_config["learning"]["exploration_decay"],
            "min_exploration_rate": raw_config["learning"]["min_exploration_rate"],
            "episodes": raw_config.get("training", {}).get("num_episodes", 500),
        }
    
    return config


def train_text_cnn(config: dict, train_df, val_df, test_df, vectorizer):
    """Train Text-CNN model"""
    logger.info("=" * 50)
    logger.info("TRAINING TEXT-CNN MODEL")
    logger.info("=" * 50)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Prepare data
    train_x = vectorizer.encode_batch(train_df["text"].tolist())
    train_y = train_df["label"].values
    val_x = vectorizer.encode_batch(val_df["text"].tolist())
    val_y = val_df["label"].values
    test_x = vectorizer.encode_batch(test_df["text"].tolist())
    test_y = test_df["label"].values
    
    # Convert to tensors
    train_x = torch.LongTensor(train_x)
    train_y = torch.LongTensor(train_y)
    val_x = torch.LongTensor(val_x)
    val_y = torch.LongTensor(val_y)
    test_x = torch.LongTensor(test_x)
    test_y = torch.LongTensor(test_y)
    
    # Create dataloaders
    train_dataset = TensorDataset(train_x, train_y)
    val_dataset = TensorDataset(val_x, val_y)
    test_dataset = TensorDataset(test_x, test_y)
    
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config["batch_size"])
    test_loader = DataLoader(test_dataset, batch_size=config["batch_size"])
    
    # Create model
    model = TextCNN(
        vocab_size=vectorizer.vocab_size,
        embedding_dim=config["embedding_dim"],
        num_classes=config["num_classes"],
        num_filters=config["num_filters"],
        filter_sizes=config["filter_sizes"],
        dropout_rate=config["dropout_rate"]
    ).to(device)
    
    logger.info(f"Model: {model}")
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])
    
    # Training loop
    best_val_acc = 0
    patience = config.get("early_stopping_patience", 5)
    patience_counter = 0
    
    for epoch in range(config["epochs"]):
        # Train
        train_loss = TrainingUtils.train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validate
        val_loss, val_acc, _, _ = TrainingUtils.evaluate(model, val_loader, criterion, device)
        
        logger.info(f"Epoch {epoch+1}/{config['epochs']} | "
                   f"Train Loss: {train_loss:.4f} | "
                   f"Val Loss: {val_loss:.4f} | "
                   f"Val Acc: {val_acc:.4f}")
        
        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # Save best model
            weights_dir = Path("weights")
            weights_dir.mkdir(exist_ok=True)
            torch.save(model.state_dict(), weights_dir / "text_cnn_best.pt")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping after {epoch+1} epochs")
                break
    
    # Test
    test_loss, test_acc, test_preds, test_labels = TrainingUtils.evaluate(
        model, test_loader, criterion, device
    )
    
    logger.info("=" * 50)
    logger.info("TEST RESULTS")
    logger.info("=" * 50)
    logger.info(f"Test Loss: {test_loss:.4f}")
    logger.info(f"Test Accuracy: {test_acc:.4f}")
    
    # Calculate F1-scores
    from sklearn.metrics import f1_score, confusion_matrix
    macro_f1 = f1_score(test_labels, test_preds, average="macro")
    logger.info(f"Macro-F1: {macro_f1:.4f}")
    
    # Save results
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "model": "text_cnn",
        "test_loss": float(test_loss),
        "test_accuracy": float(test_acc),
        "macro_f1": float(macro_f1),
        "num_classes": 8,
        "config": config
    }
    
    with open(results_dir / "text_cnn_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Save confusion matrix
    cm = confusion_matrix(test_labels, test_preds)
    conf_matrix_path = results_dir / "text_cnn_confusion_matrix.npy"
    np.save(conf_matrix_path, cm)
    logger.info(f"Confusion matrix saved to {conf_matrix_path}")
    
    return model, results


def train_rl_agent(config: dict) -> QLearningAgent:
    """Train Q-Learning agent"""
    logger.info("=" * 50)
    logger.info("TRAINING Q-LEARNING AGENT")
    logger.info("=" * 50)
    
    agent = QLearningAgent(
        num_states=8,
        learning_rate=config.get("learning_rate", 0.1),
        discount_factor=config.get("discount_factor", 0.9),
        exploration_rate=config.get("exploration_rate", 0.3),
        exploration_decay=config.get("exploration_decay", 0.995)
    )
    
    # Train
    history = agent.train(episodes=config.get("num_episodes", 1000))
    
    # Statistics
    stats = agent.get_statistics()
    logger.info("=" * 50)
    logger.info("RL TRAINING STATISTICS")
    logger.info("=" * 50)
    logger.info(json.dumps(stats, indent=2))
    
    # Save agent
    weights_dir = Path("weights")
    weights_dir.mkdir(exist_ok=True)
    agent.save(weights_dir / "q_learning_agent.json")
    
    # Save history (convert numpy types to native Python types)
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert numpy types to native Python types
    history_serializable = {}
    for key, value in history.items():
        if isinstance(value, list):
            history_serializable[key] = [float(x) if hasattr(x, 'item') else x for x in value]
        else:
            history_serializable[key] = float(value) if hasattr(value, 'item') else value
    
    with open(results_dir / "rl_training_history.json", "w") as f:
        json.dump(history_serializable, f, indent=2)
    
    return agent


def main():
    """Main training pipeline"""
    logger.info("Starting Helpify AI Training Pipeline...")
    
    # Load config
    config_path = "experiments/configs/text_cnn.yaml"
    config = load_config(config_path)
    
    # Data pipeline
    logger.info("Loading dataset...")
    dataset = Dataset()
    train_df, val_df, test_df = dataset.prepare_pipeline(seed=42)
    
    # Build vocabulary
    logger.info("Building vocabulary...")
    vectorizer = TextVectorizer(
        vocab_size=config.get("vocab_size", 5000),
        max_length=config.get("max_length", 50)
    )
    vectorizer.build_vocab(train_df["text"].tolist())
    
    # Train CNN
    logger.info("Training Text-CNN...")
    cnn_model, cnn_results = train_text_cnn(config, train_df, val_df, test_df, vectorizer)
    
    # Train RL agent
    logger.info("Training RL Agent...")
    rl_config = load_config("experiments/configs/rl_agent.yaml", config_type="rl")
    rl_agent = train_rl_agent(rl_config)
    
    logger.info("=" * 50)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 50)
    
    # Save vectorizer
    import pickle
    with open("weights/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    logger.info("All models and configs saved to weights/ directory")


if __name__ == "__main__":
    main()
