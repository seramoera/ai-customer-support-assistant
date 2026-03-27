#!/usr/bin/env python
"""Helpify AI Backend API with hybrid routing.

Known in-domain queries are handled by Text-CNN + Q-Learning.
Open-domain/low-confidence queries are handled by retrieval-augmented response.
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch

sys.path.insert(0, '.')

from src.data_pipeline import Dataset, TextVectorizer
from src.models.text_cnn import TextCNN
from src.rl.q_learning import QLearningAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

models: Dict[str, object] = {}
sessions: Dict[str, List[Dict[str, str]]] = {}

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "experiments" / "logs"
KB_DIR = BASE_DIR / "data" / "kb"
INTERACTION_LOG_PATH = LOG_DIR / "chat_events.jsonl"

INTENTS = [
    "borrow_money", "cancel_subscription", "report_fraud",
    "account_blocked", "shopping_assistance", "what_is_butts",
    "airline_baggage_policy", "international_visa",
    "restaurant_reservation", "schedule_maintenance"
]

ACTIONS = [
    "ask_order_id", "provide_solution", "escalate_human",
    "give_faq", "ask_clarification", "apologize_and_help"
]

RESPONSE_TEMPLATES = {
    "ask_order_id": "Could you please provide your order or reference number?",
    "provide_solution": "Based on your inquiry, here's what I can help with: {context}",
    "escalate_human": "I'm connecting you with a specialist who can better assist you.",
    "give_faq": "This is a common question. Here's what you should know: {context}",
    "ask_clarification": "Could you provide more details about your issue?",
    "apologize_and_help": "I sincerely apologize for the inconvenience. Let me help you resolve this."
}

DEFAULT_KB = [
    {
        "title": "Subscription & Billing",
        "content": "You can cancel a subscription from account settings. Refund windows depend on plan type and local law."
    },
    {
        "title": "Account Security",
        "content": "For suspected fraud, lock the account immediately, rotate credentials, and contact support with timestamps."
    },
    {
        "title": "Travel Policies",
        "content": "Airline baggage allowances vary by route and fare class. International visa requirements depend on passport and destination."
    },
    {
        "title": "Maintenance & Scheduling",
        "content": "Schedule maintenance by selecting preferred date/time and confirming service address and issue details."
    },
]

ROUTER_CFG = {
    "intent_confidence_threshold": 0.74,
    "intent_margin_threshold": 0.16,
    "retrieval_similarity_threshold": 0.20,
    "memory_turns": 6,
}


def ensure_paths() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)


def append_event(event: Dict[str, object]) -> None:
    ensure_paths()
    payload = {"timestamp": datetime.utcnow().isoformat() + "Z", **event}
    with INTERACTION_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def ensure_default_kb() -> None:
    ensure_paths()
    default_file = KB_DIR / "base_support_kb.json"
    if default_file.exists():
        return
    with default_file.open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_KB, f, ensure_ascii=True, indent=2)


def load_kb_documents() -> List[Dict[str, str]]:
    ensure_default_kb()
    docs: List[Dict[str, str]] = []

    for path in KB_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                items = json.load(f)
            if isinstance(items, list):
                for item in items:
                    title = str(item.get("title", path.stem))
                    content = str(item.get("content", "")).strip()
                    if content:
                        docs.append({"title": title, "content": content})
        except Exception as e:
            logger.warning("Failed to read KB file %s: %s", path, e)

    for path in KB_DIR.glob("*.md"):
        try:
            content = path.read_text(encoding="utf-8").strip()
            if content:
                docs.append({"title": path.stem, "content": content})
        except Exception as e:
            logger.warning("Failed to read KB markdown %s: %s", path, e)

    return docs


def build_retriever() -> None:
    docs = load_kb_documents()
    corpus = [f"{d['title']}\n{d['content']}" for d in docs]
    tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = tfidf.fit_transform(corpus) if corpus else None

    models["kb_docs"] = docs
    models["kb_tfidf"] = tfidf
    models["kb_matrix"] = matrix
    logger.info("✓ Retriever loaded (%d docs)", len(docs))


def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, object]]:
    docs = models.get("kb_docs", [])
    tfidf = models.get("kb_tfidf")
    matrix = models.get("kb_matrix")
    if not docs or matrix is None or tfidf is None:
        return []

    qv = tfidf.transform([query])
    scores = cosine_similarity(qv, matrix)[0]
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

    out: List[Dict[str, object]] = []
    for idx, score in ranked:
        out.append({
            "title": docs[idx]["title"],
            "content": docs[idx]["content"],
            "score": float(score),
        })
    return out


def load_models() -> None:
    logger.info("Loading trained models...")
    ensure_paths()

    dataset = Dataset()
    train_df = pd.read_csv("data/processed/train.csv")
    vectorizer = TextVectorizer(vocab_size=5000, max_length=50)
    vectorizer.build_vocab(train_df["text"].tolist())
    models["vectorizer"] = vectorizer
    models["dataset"] = dataset
    logger.info("✓ Vectorizer loaded")

    cnn_model = TextCNN(
        vocab_size=5000,
        embedding_dim=300,
        num_classes=10,
        num_filters=100,
        filter_sizes=[2, 3, 4],
        dropout_rate=0.5,
    )
    cnn_model.load_state_dict(torch.load("weights/text_cnn_best.pt", map_location="cpu", weights_only=True))
    cnn_model.eval()
    models["cnn"] = cnn_model
    logger.info("✓ Text-CNN model loaded")

    rl_agent = QLearningAgent(num_states=10)
    rl_agent.load("weights/q_learning_agent.json")
    models["rl"] = rl_agent
    logger.info("✓ Q-Learning agent loaded")

    build_retriever()
    logger.info("✅ All models ready!")


def predict_intent_action(user_text: str) -> Dict[str, object]:
    dataset = models["dataset"]
    vectorizer = models["vectorizer"]
    preprocessed = dataset.preprocess(user_text)

    encoded = vectorizer.encode(preprocessed)
    encoded_batch = torch.LongTensor([encoded])

    cnn = models["cnn"]
    with torch.no_grad():
        logits, probs = cnn(encoded_batch)
        sorted_probs, sorted_ids = torch.sort(probs[0], descending=True)
        intent_id = int(sorted_ids[0].item())
        confidence = float(sorted_probs[0].item())
        margin = float(sorted_probs[0].item() - sorted_probs[1].item())

    intent_name = INTENTS[intent_id]
    rl_agent = models["rl"]
    action_id = rl_agent.select_action(intent_id, training=False)
    action_name = ACTIONS[action_id]

    return {
        "preprocessed": preprocessed,
        "intent_id": intent_id,
        "intent": intent_name,
        "confidence": confidence,
        "margin": margin,
        "action_id": action_id,
        "action": action_name,
    }


def build_memory_context(session_id: str) -> str:
    turns = sessions.get(session_id, [])[-ROUTER_CFG["memory_turns"]:]
    lines = []
    for item in turns:
        role = item.get("role", "user")
        content = item.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def build_open_response(user_text: str, retrieved: List[Dict[str, object]], memory_context: str) -> str:
    if not retrieved:
        return (
            "I can help with a broad range of questions, but I need a bit more detail to answer accurately. "
            "Could you share the exact product, policy, or scenario you mean?"
        )

    top = retrieved[0]
    base = top["content"].strip().replace("\n", " ")
    snippet = base[:320] + ("..." if len(base) > 320 else "")
    if memory_context:
        return (
            f"Based on your question and earlier context, here is the best guidance from {top['title']}: "
            f"{snippet} If you want, I can tailor this to your exact situation in one step."
        )
    return (
        f"Here is the most relevant guidance from {top['title']}: {snippet} "
        "If you share a bit more context, I can make this more specific to your case."
    )


def route_mode(pred: Dict[str, object], retrieved: List[Dict[str, object]]) -> str:
    conf = float(pred["confidence"])
    margin = float(pred["margin"])
    top_sim = float(retrieved[0]["score"]) if retrieved else 0.0
    if conf >= ROUTER_CFG["intent_confidence_threshold"] and margin >= ROUTER_CFG["intent_margin_threshold"]:
        return "intent_rl"
    if top_sim >= ROUTER_CFG["retrieval_similarity_threshold"]:
        return "open_rag"
    return "clarify"


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "system": "Helpify AI",
        "models_loaded": len(models) > 0,
        "intents": len(INTENTS),
        "actions": len(ACTIONS),
        "kb_docs": len(models.get("kb_docs", [])),
    }), 200


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() or {}
        user_text = str(data.get('text', '')).strip()
        if not user_text:
            return jsonify({"error": "Empty text"}), 400

        pred = predict_intent_action(user_text)
        response = RESPONSE_TEMPLATES.get(pred["action"], f"I'm here to help with your {pred['intent']} request.")
        if "{context}" in response:
            response = response.format(context=pred["intent"].replace("_", " "))

        return jsonify({
            "success": True,
            "mode": "intent_rl",
            "input": user_text,
            "preprocessed": pred["preprocessed"],
            "intent": pred["intent"],
            "intent_id": pred["intent_id"],
            "confidence": pred["confidence"],
            "margin": pred["margin"],
            "action": pred["action"],
            "action_id": pred["action_id"],
            "response": response,
        }), 200
    except Exception as e:
        logger.error("Prediction error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Hybrid endpoint for intent+RL and open-domain retrieval behavior."""
    try:
        data = request.get_json() or {}
        user_text = str(data.get("text", "")).strip()
        session_id = str(data.get("session_id", "default"))
        incoming_history = data.get("history", [])

        if not user_text:
            return jsonify({"error": "Empty text"}), 400

        if session_id not in sessions:
            sessions[session_id] = []

        if isinstance(incoming_history, list) and not sessions[session_id]:
            for item in incoming_history[-ROUTER_CFG["memory_turns"]:]:
                role = str(item.get("role", "user"))
                content = str(item.get("content", ""))
                if content:
                    sessions[session_id].append({"role": role, "content": content})

        pred = predict_intent_action(user_text)
        retrieved = retrieve_context(user_text, top_k=3)
        mode = route_mode(pred, retrieved)

        memory_context = build_memory_context(session_id)
        if mode == "intent_rl":
            action = pred["action"]
            response = RESPONSE_TEMPLATES.get(action, f"I'm here to help with your {pred['intent']} request.")
            if "{context}" in response:
                response = response.format(context=pred["intent"].replace("_", " "))
            reward = 2 if pred["confidence"] >= 0.85 else 1
        elif mode == "open_rag":
            action = "provide_solution"
            response = build_open_response(user_text, retrieved, memory_context)
            reward = 1
        else:
            action = "ask_clarification"
            response = (
                "I can help with that. To give a precise answer, could you share one extra detail "
                "about your goal or situation?"
            )
            reward = 0

        sessions[session_id].append({"role": "user", "content": user_text})
        sessions[session_id].append({"role": "assistant", "content": response})
        sessions[session_id] = sessions[session_id][-2 * ROUTER_CFG["memory_turns"]:]

        event = {
            "session_id": session_id,
            "mode": mode,
            "text": user_text,
            "intent": pred["intent"],
            "confidence": pred["confidence"],
            "margin": pred["margin"],
            "action": action,
            "retrieval_top_score": float(retrieved[0]["score"]) if retrieved else 0.0,
        }
        append_event(event)

        return jsonify({
            "success": True,
            "mode": mode,
            "session_id": session_id,
            "intent": pred["intent"],
            "intent_confidence": pred["confidence"],
            "intent_margin": pred["margin"],
            "cnn_features": [pred["intent"], "confidence", f"{pred['confidence']:.3f}"],
            "rl_action": action,
            "rl_reward": reward,
            "response": response,
            "retrieval": [
                {
                    "title": r["title"],
                    "score": round(float(r["score"]), 4)
                }
                for r in retrieved
            ],
            "model_metrics": {
                "accuracy": 0.9667,
                "macro_f1": 0.9662,
            },
        }), 200
    except Exception as e:
        logger.error("Chat error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({
        "models": {
            "nlu": {
                "name": "Text-CNN",
                "architecture": "Conv1d [2,3,4-grams] + MaxPool + FC",
                "embedding_dim": 300,
                "vocab_size": 5000,
                "num_filters": 100,
                "num_classes": 10,
            },
            "rl": {
                "name": "Q-Learning",
                "algorithm": "Tabular Q-Learning",
                "num_states": 10,
                "num_actions": 6,
                "learning_rate": 0.1,
                "discount_factor": 0.9,
            },
            "retrieval": {
                "name": "TF-IDF Retriever",
                "docs_loaded": len(models.get("kb_docs", [])),
                "top_k": 3,
            },
        },
        "router": ROUTER_CFG,
        "intents": INTENTS,
        "actions": ACTIONS,
        "performance": {
            "cnn_accuracy": 0.9667,
            "cnn_macro_f1": 0.9662,
            "rl_success_rate": 0.727,
            "rl_avg_reward": 0.946,
        },
    }), 200


@app.route('/api/intents', methods=['GET'])
def get_intents():
    return jsonify({
        "intents": INTENTS,
        "count": len(INTENTS),
        "actions": ACTIONS,
        "action_count": len(ACTIONS),
    }), 200


@app.route('/api/retrain/signals', methods=['GET'])
def retrain_signals():
    """Expose counts of low-confidence/open-domain events for active learning."""
    if not INTERACTION_LOG_PATH.exists():
        return jsonify({"events": 0, "low_confidence": 0, "open_rag": 0, "clarify": 0}), 200

    events = 0
    low_conf = 0
    open_rag = 0
    clarify = 0
    with INTERACTION_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
            except Exception:
                continue
            events += 1
            if float(item.get("confidence", 0.0)) < ROUTER_CFG["intent_confidence_threshold"]:
                low_conf += 1
            mode = item.get("mode")
            if mode == "open_rag":
                open_rag += 1
            if mode == "clarify":
                clarify += 1

    return jsonify({
        "events": events,
        "low_confidence": low_conf,
        "open_rag": open_rag,
        "clarify": clarify,
    }), 200


if __name__ == '__main__':
    load_models()

    logger.info("\n" + "=" * 70)
    logger.info("HELPIFY AI API SERVER")
    logger.info("=" * 70)
    logger.info("Starting server at http://localhost:5000")
    logger.info("API Documentation:")
    logger.info("  POST /api/predict          - Intent+RL only")
    logger.info("  POST /api/chat             - Hybrid router (intent + open-domain)")
    logger.info("  GET  /api/health           - Health check")
    logger.info("  GET  /api/models           - Model and router info")
    logger.info("  GET  /api/intents          - Intent classes")
    logger.info("  GET  /api/retrain/signals  - Active-learning stats")
    logger.info("=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
