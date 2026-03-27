"""
Text-CNN Model for Intent Classification
Based on: Yoon Kim (2014) "Convolutional Neural Networks for Sentence Classification"
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class TextCNN(nn.Module):
    """
    Text-CNN Model
    
    Architecture:
    Input → Embedding → Conv1d (multiple filter sizes) → MaxPool → Dropout → FC → Output
    """
    
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 300,
        num_classes: int = 8,
        num_filters: int = 100,
        filter_sizes: List[int] = None,
        dropout_rate: float = 0.5,
        pre_trained_embeddings: np.ndarray = None
    ):
        super(TextCNN, self).__init__()
        
        if filter_sizes is None:
            filter_sizes = [2, 3, 4]
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        self.num_filters = num_filters
        self.filter_sizes = filter_sizes
        
        # Embedding layer
        if pre_trained_embeddings is not None:
            self.embedding = nn.Embedding.from_pretrained(
                torch.FloatTensor(pre_trained_embeddings),
                freeze=False
            )
        else:
            self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # Convolutional layers (one for each filter size)
        self.convs = nn.ModuleList([
            nn.Conv1d(
                in_channels=embedding_dim,
                out_channels=num_filters,
                kernel_size=fs
            )
            for fs in filter_sizes
        ])
        
        # Dropout
        self.dropout = nn.Dropout(dropout_rate)
        
        # Fully connected layer
        self.fc = nn.Linear(len(filter_sizes) * num_filters, num_classes)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: (batch_size, seq_length)
        
        Returns:
            logits: (batch_size, num_classes)
            probs: (batch_size, num_classes)
        """
        # Embedding: (batch_size, seq_length) → (batch_size, seq_length, embedding_dim)
        x = self.embedding(x)
        
        # Transpose for Conv1d: (batch_size, embedding_dim, seq_length)
        x = x.transpose(1, 2)
        
        # Apply convolutions and pooling
        conv_outputs = []
        for conv in self.convs:
            # Conv: (batch_size, num_filters, seq_length - kernel_size + 1)
            conv_out = F.relu(conv(x))
            
            # Max pool: (batch_size, num_filters)
            pool_out = F.max_pool1d(conv_out, conv_out.size(2))
            pool_out = pool_out.squeeze(2)
            
            conv_outputs.append(pool_out)
        
        # Concatenate all outputs: (batch_size, len(filter_sizes) * num_filters)
        x = torch.cat(conv_outputs, dim=1)
        
        # Dropout
        x = self.dropout(x)
        
        # Fully connected
        logits = self.fc(x)
        
        # Softmax probabilities
        probs = F.softmax(logits, dim=1)
        
        return logits, probs
    
    def predict(self, x: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prediction mode (returns probabilities and predicted classes)
        
        Args:
            x: (batch_size, seq_length)
        
        Returns:
            predictions: (batch_size,) predicted class indices
            confidences: (batch_size,) confidence scores
        """
        with torch.no_grad():
            _, probs = self.forward(x)
            confidences, predictions = torch.max(probs, dim=1)
        
        return predictions.cpu().numpy(), confidences.cpu().numpy()


class BaselineModel(nn.Module):
    """
    Baseline Model: Logistic Regression on top of TF-IDF
    
    For comparison with CNN.
    In practice, we'll use sklearn's LogisticRegression.
    This is just for consistency in the PyTorch framework.
    """
    
    def __init__(self, input_dim: int, num_classes: int):
        super(BaselineModel, self).__init__()
        self.fc = nn.Linear(input_dim, num_classes)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass (x should be TF-IDF features)"""
        logits = self.fc(x)
        probs = F.softmax(logits, dim=1)
        return logits, probs
    
    def predict(self, x: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """Prediction mode"""
        with torch.no_grad():
            _, probs = self.forward(x)
            confidences, predictions = torch.max(probs, dim=1)
        
        return predictions.cpu().numpy(), confidences.cpu().numpy()


class TrainingUtils:
    """Training utilities"""
    
    @staticmethod
    def train_epoch(
        model: nn.Module,
        dataloader,
        criterion,
        optimizer,
        device: str = "cpu"
    ) -> float:
        """Train one epoch"""
        model.train()
        total_loss = 0
        
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            # Forward pass
            logits, _ = model(batch_x)
            loss = criterion(logits, batch_y)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(dataloader)
    
    @staticmethod
    def evaluate(
        model: nn.Module,
        dataloader,
        criterion,
        device: str = "cpu"
    ) -> Tuple[float, float, np.ndarray, np.ndarray]:
        """Evaluate model"""
        model.eval()
        total_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                
                logits, _ = model(batch_x)
                loss = criterion(logits, batch_y)
                total_loss += loss.item()
                
                preds, _ = model.predict(batch_x)
                all_preds.extend(preds)
                all_labels.extend(batch_y.cpu().numpy())
        
        avg_loss = total_loss / len(dataloader)
        accuracy = np.mean(np.array(all_preds) == np.array(all_labels))
        
        return avg_loss, accuracy, np.array(all_preds), np.array(all_labels)


if __name__ == "__main__":
    # Test model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model = TextCNN(
        vocab_size=5000,
        embedding_dim=300,
        num_classes=8,
        num_filters=100,
        filter_sizes=[2, 3, 4]
    ).to(device)
    
    # Sample input
    x = torch.randint(0, 5000, (32, 50))  # batch_size=32, seq_length=50
    logits, probs = model(x)
    
    print(f"Model: {model}")
    print(f"Input shape: {x.shape}")
    print(f"Logits shape: {logits.shape}")
    print(f"Probs shape: {probs.shape}")
    print(f"Sum of probs (should be 1): {probs[0].sum().item():.4f}")
