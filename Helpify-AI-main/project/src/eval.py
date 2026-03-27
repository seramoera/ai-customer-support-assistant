"""
Evaluation Script - Metrics and Error Analysis
"""

import torch
import numpy as np
import json
import logging
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, 
    confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

from data_pipeline import Dataset, TextVectorizer
from models.text_cnn import TextCNN

logger = logging.getLogger(__name__)


def evaluate_model(model_path: str, test_df, vectorizer) -> dict:
    """Evaluate trained model"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load model
    model = TextCNN(vocab_size=vectorizer.vocab_size)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    # Prepare test data
    test_x = vectorizer.encode_batch(test_df["text"].tolist())
    test_y = test_df["label"].values
    test_x = torch.LongTensor(test_x).to(device)
    
    # Predict
    with torch.no_grad():
        predictions, confidences = model.predict(test_x)
    
    # Metrics
    accuracy = accuracy_score(test_y, predictions)
    macro_f1 = f1_score(test_y, predictions, average="macro")
    weighted_f1 = f1_score(test_y, predictions, average="weighted")
    precision = precision_score(test_y, predictions, average="macro")
    recall = recall_score(test_y, predictions, average="macro")
    
    # Confusion matrix
    cm = confusion_matrix(test_y, predictions)
    
    # Classification report
    class_report = classification_report(
        test_y, predictions,
        target_names=Dataset.INTENTS,
        output_dict=True
    )
    
    results = {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "precision": float(precision),
        "recall": float(recall),
        "confusion_matrix": cm.tolist(),
        "classification_report": class_report
    }
    
    logger.info("=" * 50)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Accuracy: {accuracy:.4f}")
    logger.info(f"Macro-F1: {macro_f1:.4f}")
    logger.info(f"Weighted-F1: {weighted_f1:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    
    return results, predictions, test_y


def error_analysis(predictions, test_y, test_df, vectorizer) -> dict:
    """Analyze misclassified examples"""
    misclassified = predictions != test_y
    misclassified_indices = np.where(misclassified)[0]
    
    analysis = {
        "total_errors": int(np.sum(misclassified)),
        "error_rate": float(np.mean(misclassified)),
        "misclassified_examples": []
    }
    
    # Get sample errors
    for idx in misclassified_indices[:10]:  # First 10 errors
        example = {
            "text": test_df.iloc[idx]["text"],
            "true_intent": Dataset.INTENTS[test_y[idx]],
            "predicted_intent": Dataset.INTENTS[predictions[idx]],
            "row_index": int(idx)
        }
        analysis["misclassified_examples"].append(example)
    
    logger.info("\nSample Misclassified Examples:")
    for ex in analysis["misclassified_examples"][:5]:
        logger.info(f"  Text: {ex['text']}")
        logger.info(f"  True: {ex['true_intent']} → Predicted: {ex['predicted_intent']}")
    
    return analysis


def plot_confusion_matrix(cm: np.ndarray, save_path: str = None):
    """Plot confusion matrix"""
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=Dataset.INTENTS,
                yticklabels=Dataset.INTENTS,
                cbar_kws={"label": "Count"})
    plt.title("Confusion Matrix - Text-CNN Intent Classification")
    plt.ylabel("True Intent")
    plt.xlabel("Predicted Intent")
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved confusion matrix to {save_path}")
    
    plt.close()


def main():
    """Full evaluation"""
    logging.basicConfig(level=logging.INFO)
    
    # Load data
    dataset = Dataset()
    _, _, test_df = dataset.prepare_pipeline(seed=42)
    
    # Load vectorizer
    import pickle
    with open("weights/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    
    # Evaluate
    results, predictions, test_y = evaluate_model(
        "weights/text_cnn_best.pt",
        test_df,
        vectorizer
    )
    
    # Error analysis
    error_analysis_results = error_analysis(predictions, test_y, test_df, vectorizer)
    
    # Save results
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    with open(results_dir / "evaluation_metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open(results_dir / "error_analysis.json", "w") as f:
        json.dump(error_analysis_results, f, indent=2)
    
    # Plot confusion matrix
    cm = np.array(results["confusion_matrix"])
    plot_confusion_matrix(cm, results_dir / "confusion_matrix.png")
    
    logger.info("Evaluation complete!")
    logger.info(f"Results saved to {results_dir}/")


if __name__ == "__main__":
    main()
