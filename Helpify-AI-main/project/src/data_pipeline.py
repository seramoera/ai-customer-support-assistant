"""
Data Pipeline
Handles loading, preprocessing, and splitting datasets
Uses CLINC150 dataset - optimized for intent classification
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict
import urllib.request
from urllib.error import URLError
import logging

logger = logging.getLogger(__name__)

# CLINC150 subset - 10 representative intents for chatbot/support
CLINC150_SUBSET_INTENTS = [
    "borrow_money",
    "cancel_subscription",
    "report_fraud",
    "account_blocked",
    "shopping_assistance",
    "what_is_butts",
    "airline_baggage_policy",
    "international_visa",
    "restaurant_reservation",
    "schedule_maintenance"
]


class Dataset:
    """Intent Classification Dataset (uses CLINC150)"""
    
    # Use CLINC150 subset for better real-world performance
    INTENTS = CLINC150_SUBSET_INTENTS
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.intent_to_idx = {intent: idx for idx, intent in enumerate(self.INTENTS)}
        self.idx_to_intent = {idx: intent for intent, idx in self.intent_to_idx.items()}
    
    @staticmethod
    def create_sample_dataset():
        """Create a sample dataset (for demo/testing)"""
        data = {
            "greeting": [
                "Hello",
                "Hi there",
                "Good morning",
                "Hey",
                "Greetings"
            ],
            "order_status": [
                "Where is my order?",
                "Track my package",
                "What's my order status?",
                "When will my order arrive?",
                "Check my delivery"
            ],
            "refund_request": [
                "I want a refund",
                "Can I return this?",
                "I need my money back",
                "Request a refund for order",
                "How do I get a refund?"
            ],
            "complaint": [
                "Your service is terrible",
                "I'm very disappointed",
                "This is unacceptable",
                "Bad experience with your company",
                "I have a complaint"
            ],
            "product_inquiry": [
                "Tell me about your products",
                "What are your prices?",
                "Do you have size 10?",
                "Can you describe the features?",
                "Product information please"
            ],
            "cancel_order": [
                "Cancel my order",
                "I want to cancel",
                "Delete my order",
                "Cancelation request",
                "I don't want it anymore"
            ],
            "shipping_issue": [
                "My package hasn't arrived",
                "Shipping is delayed",
                "Where's my shipment?",
                "Late delivery",
                "Package tracking"
            ],
            "account_issue": [
                "I can't log in",
                "Account problem",
                "Forgot my password",
                "Reset my login",
                "Account access issue"
            ]
        }
        
        samples = []
        for intent, queries in data.items():
            for query in queries:
                samples.append({"text": query, "intent": intent})
        
        return pd.DataFrame(samples)
    
    @staticmethod
    def download_clinc150():
        """Download CLINC150 dataset from Hugging Face"""
        try:
            from datasets import load_dataset
            
            logger.info("Downloading CLINC150 dataset from Hugging Face...")
            
            # Load CLINC150 dataset
            dataset = load_dataset("clinc_oos", "plus")
            
            # Extract train set and convert to DataFrame
            df_list = []
            
            for split_name in ["train", "validation", "test"]:
                if split_name in dataset:
                    split = dataset[split_name]
                    
                    for sample in split:
                        intent_id = sample["intent"]
                        intent_name = split.features["intent"].int2str(intent_id)
                        
                        df_list.append({
                            "text": sample["text"],
                            "intent": intent_name,
                            "split": split_name
                        })
            
            df = pd.DataFrame(df_list)
            
            # Filter to subset of intents for better performance
            df = df[df["intent"].isin(CLINC150_SUBSET_INTENTS)].reset_index(drop=True)
            
            logger.info(f"Downloaded {len(df)} samples from {len(df['intent'].unique())} intent classes")
            logger.info(f"Sample intents: {df['intent'].unique()[:5].tolist()}")
            
            return df
            
        except ImportError:
            logger.warning("datasets library not found. Install with: pip install datasets")
            logger.info("Falling back to sample dataset...")
            return Dataset.create_sample_dataset()
        except Exception as e:
            logger.warning(f"Failed to download CLINC150: {e}")
            logger.info("Falling back to sample dataset...")
            return Dataset.create_sample_dataset()
    
    def load_data(self) -> pd.DataFrame:
        """Load or create dataset"""
        processed_file = self.data_dir / "data.csv"
        
        if processed_file.exists():
            logger.info(f"Loading from {processed_file}")
            return pd.read_csv(processed_file)
        
        logger.info("Downloading CLINC150 dataset...")
        df = self.download_clinc150()
        
        # Save for future use
        df.to_csv(processed_file, index=False)
        logger.info(f"Saved dataset to {processed_file}")
        return df
    
    def preprocess(self, text: str) -> str:
        """Preprocess text"""
        # Lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        import re
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        
        # Remove extra spaces
        text = " ".join(text.split())
        
        return text
    
    def split_data(self, df: pd.DataFrame, 
                   train_ratio: float = 0.7,
                   val_ratio: float = 0.15,
                   test_ratio: float = 0.15,
                   seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into train/val/test"""
        
        # Check if dataset has pre-existing splits (from CLINC150)
        if "split" in df.columns:
            logger.info("Using pre-existing dataset splits from CLINC150...")
            train = df[df["split"] == "train"].drop("split", axis=1).reset_index(drop=True)
            val = df[df["split"] == "validation"].drop("split", axis=1).reset_index(drop=True)
            test = df[df["split"] == "test"].drop("split", axis=1).reset_index(drop=True)
            
            # If any split is empty, fall back to random split
            if len(train) == 0 or len(val) == 0 or len(test) == 0:
                logger.warning("Some splits are empty, using random split instead...")
                df = df.drop("split", axis=1)
                df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
                n = len(df)
                train_idx = int(n * train_ratio)
                val_idx = int(n * (train_ratio + val_ratio))
                
                train = df.iloc[:train_idx]
                val = df.iloc[train_idx:val_idx]
                test = df.iloc[val_idx:]
        else:
            logger.info("Using random split...")
            np.random.seed(seed)
            
            # Shuffle
            df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
            
            n = len(df)
            train_idx = int(n * train_ratio)
            val_idx = int(n * (train_ratio + val_ratio))
            
            train = df.iloc[:train_idx]
            val = df.iloc[train_idx:val_idx]
            test = df.iloc[val_idx:]
        
        logger.info(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        
        return train, val, test
    
    def encode_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode intent labels to indices"""
        df = df.copy()
        df["label"] = df["intent"].map(self.intent_to_idx)
        return df
    
    def prepare_pipeline(self, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Full preprocessing pipeline"""
        logger.info("Starting data pipeline...")
        
        # Load
        df = self.load_data()
        logger.info(f"Loaded {len(df)} samples")
        
        # Preprocess text
        df["text"] = df["text"].apply(self.preprocess)
        logger.info("Preprocessed text")
        
        # Encode labels
        df = self.encode_labels(df)
        logger.info("Encoded labels")
        
        # Split
        train, val, test = self.split_data(df, seed=seed)
        
        # Save splits
        train.to_csv(self.data_dir / "train.csv", index=False)
        val.to_csv(self.data_dir / "val.csv", index=False)
        test.to_csv(self.data_dir / "test.csv", index=False)
        
        logger.info("Data pipeline complete!")
        return train, val, test


class TextVectorizer:
    """Convert text to vectors (embeddings)"""
    
    def __init__(self, vocab_size: int = 5000, max_length: int = 50):
        self.vocab_size = vocab_size
        self.max_length = max_length
        self.word_index = {}
        self.index_word = {}
    
    def build_vocab(self, texts: List[str]):
        """Build vocabulary from texts"""
        words = set()
        for text in texts:
            words.update(text.split())
        
        # Create word index
        for idx, word in enumerate(sorted(words)[:self.vocab_size-1], 1):
            self.word_index[word] = idx
            self.index_word[idx] = word
        
        logger.info(f"Built vocab with {len(self.word_index)} words")
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text to indices"""
        indices = []
        for word in text.split():
            idx = self.word_index.get(word, 0)  # 0 = unknown
            indices.append(idx)
        
        # Pad or truncate
        if len(indices) < self.max_length:
            indices = indices + [0] * (self.max_length - len(indices))
        else:
            indices = indices[:self.max_length]
        
        return np.array(indices)
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode batch of texts"""
        return np.array([self.encode(text) for text in texts])
    
    def decode(self, indices: np.ndarray) -> str:
        """Decode indices back to text"""
        words = []
        for idx in indices:
            if idx > 0:
                words.append(self.index_word.get(idx, ""))
        return " ".join(words)


if __name__ == "__main__":
    # Test pipeline
    logging.basicConfig(level=logging.INFO)
    
    dataset = Dataset()
    train, val, test = dataset.prepare_pipeline()
    
    # Build vocabulary
    vectorizer = TextVectorizer()
    vectorizer.build_vocab(train["text"].tolist())
    
    # Encode sample
    sample_text = "I want a refund for my order"
    preprocessed = dataset.preprocess(sample_text)
    encoded = vectorizer.encode(preprocessed)
    print(f"Original: {sample_text}")
    print(f"Preprocessed: {preprocessed}")
    print(f"Encoded: {encoded}")
