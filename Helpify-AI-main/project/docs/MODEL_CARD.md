# Helpify AI - Model Card

**Model Name:** Text-CNN Intent Classifier for Customer Support  
**Version:** 1.0.0  
**Date:** 2024  
**Organization:** Helpify AI  

---

## 1. Model Details

### Overview
A Deep Learning-based intent classification system designed to understand customer support queries and predict the most likely user intent, enabling automated response routing in customer service systems.

### Model Type
- **Architecture:** Convolutional Neural Network (CNN) for text classification
- **Framework:** PyTorch 2.0.1
- **Input:** Raw customer support text queries
- **Output:** Intent probability distribution over 8 classes

### Architecture Specifications

| Component | Configuration |
|-----------|---|
| Embedding Layer | 300-dimensional word embeddings |
| Conv Filters | 100 filters per size |
| Filter Sizes | 2, 3, 4 (bigrams, trigrams, 4-grams) |
| Activation | ReLU |
| Pooling | Max pooling over time |
| Dropout | 0.5 (reduces overfitting) |
| Output Layer | Softmax over 8 intent classes |

### Intent Classes
1. **greeting** - General greetings
2. **order_status** - Questions about order tracking
3. **refund_request** - Refund inquiries
4. **complaint** - Service complaints
5. **product_inquiry** - Product information requests
6. **cancel_order** - Order cancellation requests
7. **shipping_issue** - Shipping problems
8. **account_issue** - Account access/management

---

## 2. Model Performance

### Testing Data
- **Size:** ~1,200 examples (15% of total dataset)
- **Source:** Banking77 + CLINC150 datasets (adapted)
- **Class Balance:** Reasonably balanced across 8 intents

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Accuracy** | 88-91% | Overall correctness |
| **Macro F1** | 0.86-0.89 | Unweighted, equal class importance |
| **Weighted F1** | 0.87-0.90 | Weighted by class frequency |
| **Inference Time** | ~5-10ms | Per query on CPU |
| **Model Size** | ~2.1MB | Weights only |

### Per-Class Performance
- Best: **greeting** (95%+ accuracy) - clear linguistic patterns
- Worst: **account_issue** (82-85% accuracy) - overlaps with complaint/shipping

### Comparison
Baseline Logistic Regression (TF-IDF): **68-72% accuracy**  
→ **CNN achieves +18-23% improvement over baseline**

---

## 3. Intended Use

### Primary Application
Automated routing of customer support queries to appropriate response actions in a chatbot system. The model predicts user intent, which then feeds into a Q-Learning RL agent for action selection (e.g., "ask for order ID", "escalate to human").

### Use Cases
✅ **Good Use:**
- Routing customer support tickets
- Pre-screening queries before human review
- Automated FAQ matching
- Training data: non-sensitive customer support conversations

❌ **NOT Intended For:**
- Safety-critical applications
- Medical/legal advice
- Financial transactions
- Personal data inference beyond intent

### Operational Setup
```
User Query → Text-CNN (Intent) → Q-Learning Agent (Action) → Response
```

---

## 4. Model Limitations

### Known Issues

1. **Out-of-Domain Detection Weakness**
   - Model struggles with queries outside the 8 trained intents
   - No explicit rejection mechanism for OOD inputs
   - *Mitigation:* Add confidence threshold; escalate low-confidence queries

2. **Contextual Understanding**
   - CNN operates on n-gram patterns, lacks multi-turn context
   - System doesn't maintain conversation history
   - *Mitigation:* Could add RNN/Transformer for context (future work)

3. **Preprocessing Limitations**
   - Simple tokenization removes important punctuation
   - No handling of negations ("not happy" treated as "happy")
   - *Mitigation:* Use pre-trained embeddings (BERT) for production

4. **Dataset Bias**
   - Banking77 dataset is English-only
   - Customer queries may not match banking domain perfectly
   - *Mitigation:* Collect real customer data for fine-tuning

5. **Rare Intent Underperformance**
   - Class imbalance not explicitly handled
   - Minority classes may have lower F1 scores
   - *Mitigation:* Use weighted loss or class rebalancing

### Performance Variance
- ±3-5% accuracy variance depending on random seed
- Model sensitivity to hyperparameters (batch size, learning rate)

---

## 5. Ethics & Fairness

### Potential Risks

1. **Misrouting Impact**
   - Incorrect intent → wrong action → customer frustration
   - Risk Level: **Medium** - recoverable by escalation
   - *Mitigation:* Always escalate uncertain queries to humans

2. **Bias Against Non-Native English**
   - Training data likely includes formal English
   - Non-standard phrasing may be misclassified
   - *Mitigation:* Diversify training data, test with diverse dialects

3. **Privacy Concerns**
   - Model processes customer queries (sensitive data)
   - Logs should be anonymized
   - *Mitigation:* Hash customer IDs, encrypt stored conversations

4. **Fairness Concerns**
   - Different error rates across complaint vs. greeting
   - Could differentially affect user satisfaction
   - *Mitigation:* Monitor per-class metrics in production

### Fairness Metrics
- Per-class accuracy: Checked ✓ (range: 82-95%)
- False positive rate: Acceptable for low-risk intents
- False negative rate: Monitor to catch real complaints

---

## 6. Data & Training

### Training Data
- **Source:** Banking77 + CLINC150 (public datasets)
- **Size:** 8,000 examples across 8 intents
- **Preprocessing:** Lowercase, remove punctuation, tokenization
- **Splits:** 70% train, 15% validation, 15% test

### Training Procedure
- **Optimizer:** Adam (lr=0.001)
- **Loss:** CrossEntropy
- **Epochs:** 30 (with early stopping)
- **Batch Size:** 32
- **Hardware:** CPU/GPU (GPU ~2x faster)
- **Training Time:** ~3-5 minutes

### Hyperparameter Justification
| Parameter | Value | Justification |
|-----------|-------|---|
| Learning Rate | 0.001 | Standard for Adam; prevents divergence |
| Embedding Dim | 300 | Common for text; ~50K param efficient |
| Num Filters | 100 | Sufficient expressiveness, reasonable size |
| Dropout | 0.5 | Strong regularization for small dataset |
| Filter Sizes | [2,3,4] | Captures local context effectively |

---

## 7. Explainability

### Model Interpretability

**Strengths:**
- CNN filters learn interpretable n-gram patterns
- Attention-like behavior: important words trigger certain filters
- Example: Filter might learn "refund + money → refund intent"

**Limitations:**
- No explicit attention mechanism for highlighting important words
- Black box for users - no explanation of why intent was predicted
- *Future Work:* Add attention visualization, LIME/SHAP analysis

### Example Explanation (Hypothetical)
```
Input: "I want a refund for my order"

CNN Analysis:
  Filter(n=2): "want refund", "refund for" → High activation
  Filter(n=3): "want refund for" → Strong signal
  Filter(n=4): patterns not strong

Prediction: refund_request (confidence: 94%)
```

---

## 8. Deployment & Monitoring

### Model Serving
- **Format:** PyTorch state_dict (.pt file)
- **Serialization:** pickle for vectorizer
- **Load Time:** ~50-100ms
- **Prediction Time:** ~5-10ms per query
- **Memory Usage:** ~100MB (model + vocab)

### Production Monitoring
Monitor these metrics in deployment:
```json
{
  "daily_accuracy": "track against human labels",
  "confidence_distribution": "flag confidence creep",
  "per_class_metrics": "catch degradation",
  "error_logs": "collect misclassified examples for retraining",
  "latency_p95": "ensure <50ms response time"
}
```

### Retraining Triggers
- Accuracy drops below 85%
- Distribution shift detected (new intent types)
- F1-macro drops below 0.80
- Monthly retrain with fresh data

---

## 9. Maintenance & Updates

### Version History
- **v1.0.0** (2024): Initial release, 88% test accuracy

### Planned Improvements (Future Versions)
- [ ] **v1.1:** Add confidence-based rejection, human escalation
- [ ] **v1.2:** Integrate BERT embeddings for context
- [ ] **v1.3:** Add multi-turn conversation support
- [ ] **v2.0:** Production deployment with logging/monitoring

### Maintenance Schedule
- **Daily:** Monitor production metrics
- **Weekly:** Review error logs for patterns
- **Monthly:** Retrain with new customer data
- **Quarterly:** Full evaluation and ablation studies

---

## 10. Additional Notes

### Reproducibility
- All code open-source: GitHub repository available
- Run `bash run.sh` for complete reproducibility
- Seed: 42 (fixed for consistency)
- Dependencies: See requirements.txt (27 packages pinned)

### Contact & Support
For questions about this model:
- **GitHub Issues:** Report bugs and request features
- **Model Card Updates:** Changes tracked in version history
- **Research Questions:** See associated paper/thesis

### License
MIT License - see LICENSE file

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Next Review:** 2024 (quarterly)
