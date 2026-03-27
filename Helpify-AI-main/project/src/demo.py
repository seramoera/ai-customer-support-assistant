"""
Interactive Demo - Complete Helpify AI System
Shows end-to-end flow: Input → NLP → RL → Output
"""

import torch
import json
import pickle
import logging
from pathlib import Path
from data_pipeline import Dataset, TextVectorizer
from models.text_cnn import TextCNN
from rl.q_learning import QLearningAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HelpifyAIDemo:
    """Complete Helpify AI System Demo"""
    
    def __init__(self):
        """Initialize system components"""
        logger.info("Initializing Helpify AI System...")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dataset = Dataset()
        
        # Load models
        self._load_vectorizer()
        self._load_cnn_model()
        self._load_rl_agent()
        
        logger.info("✓ System initialized successfully!")
    
    def _load_vectorizer(self):
        """Load text vectorizer"""
        vectorizer_path = Path("weights/vectorizer.pkl")
        if vectorizer_path.exists():
            with open(vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
            logger.info("✓ Loaded vectorizer")
        else:
            logger.warning("⚠ Vectorizer not found, creating new one...")
            self.vectorizer = TextVectorizer()
            # Build with sample data
            sample_texts = [
                "hello", "order status", "refund", "complaint",
                "product info", "cancel", "shipping", "account"
            ]
            self.vectorizer.build_vocab(sample_texts)
    
    def _load_cnn_model(self):
        """Load Text-CNN model"""
        model_path = Path("weights/text_cnn_best.pt")
        if model_path.exists():
            self.cnn_model = TextCNN(
                vocab_size=self.vectorizer.vocab_size,
                num_classes=8
            )
            self.cnn_model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.cnn_model.to(self.device)
            self.cnn_model.eval()
            logger.info("✓ Loaded Text-CNN model")
        else:
            logger.warning("⚠ CNN model not found, creating untrained model...")
            self.cnn_model = TextCNN(
                vocab_size=self.vectorizer.vocab_size,
                num_classes=8
            ).to(self.device)
    
    def _load_rl_agent(self):
        """Load Q-Learning agent"""
        agent_path = Path("weights/q_learning_agent.json")
        if agent_path.exists():
            self.rl_agent = QLearningAgent(num_states=8)
            self.rl_agent.load(str(agent_path))
            logger.info("✓ Loaded Q-Learning agent")
        else:
            logger.warning("⚠ RL agent not found, creating new agent...")
            self.rl_agent = QLearningAgent(num_states=8)
    
    def predict_intent(self, user_input: str) -> tuple:
        """
        Predict intent from user input
        
        Returns:
            (intent_name, confidence_score)
        """
        # Preprocess
        text = self.dataset.preprocess(user_input)
        
        # Encode
        encoded = self.vectorizer.encode(text)
        encoded = torch.LongTensor(encoded).unsqueeze(0).to(self.device)
        
        # Predict with CNN
        with torch.no_grad():
            pred_idx, confidence = self.cnn_model.predict(encoded)
        
        intent_name = self.dataset.idx_to_intent[int(pred_idx[0])]
        confidence = float(confidence[0])
        
        return intent_name, confidence
    
    def select_action(self, intent_name: str) -> tuple:
        """
        Select best response action using RL agent
        
        Returns:
            (action_name, q_value)
        """
        intent_idx = self.dataset.intent_to_idx[intent_name]
        action_idx = self.rl_agent.select_action(intent_idx, training=False)
        action_name = self.rl_agent.ACTIONS[action_idx]
        q_value = self.rl_agent.q_table[intent_idx, action_idx]
        
        return action_name, float(q_value)
    
    def generate_response(self, intent_name: str, action: str) -> str:
        """Generate response template based on intent and action"""
        
        responses = {
            "greeting": {
                "default": "Hello! Welcome to our support. How can I help you today?"
            },
            "order_status": {
                "ask_order_id": "Please provide your order ID so I can check the status.",
                "provide_solution": "Your order is on its way and should arrive within 2-3 business days.",
                "escalate_human": "Let me connect you with a specialist who can help with your order status."
            },
            "refund_request": {
                "ask_order_id": "I can help with your refund. Could you provide your order ID?",
                "ask_clarification": "Could you tell me more about why you'd like to return this item?",
                "escalate_human": "Let me transfer you to our refunds specialist.",
                "provide_solution": "Your refund has been processed and should appear in 3-5 business days."
            },
            "complaint": {
                "apologize_and_help": "I sincerely apologize for your experience. Let me make this right.",
                "ask_clarification": "I want to understand better. Could you describe what happened?",
                "escalate_human": "I'm escalating this to our senior support team for immediate attention.",
                "provide_solution": "Thank you for your feedback. We've made improvements based on this."
            },
            "product_inquiry": {
                "provide_solution": "We offer high-quality products with excellent customer reviews.",
                "give_faq": "Here are our frequently asked questions about this product...",
                "ask_clarification": "What specifically would you like to know about our products?"
            },
            "cancel_order": {
                "ask_order_id": "I can help cancel your order. Please provide your order ID.",
                "ask_clarification": "May I ask why you'd like to cancel?",
                "escalate_human": "Let me transfer you to someone who can cancel your order immediately."
            },
            "shipping_issue": {
                "provide_solution": "Your package is currently in transit. Tracking info: https://...",
                "ask_clarification": "How long ago did you place your order?",
                "escalate_human": "I'm escalating this to our shipping team for investigation."
            },
            "account_issue": {
                "ask_clarification": "What account issue are you experiencing?",
                "provide_solution": "Here are the steps to reset your password...",
                "escalate_human": "Let me connect you with our account support specialist."
            }
        }
        
        if intent_name in responses:
            intent_responses = responses[intent_name]
            if action in intent_responses:
                return intent_responses[action]
            elif "default" in intent_responses:
                return intent_responses["default"]
        
        return f"Thank you for your inquiry about {intent_name}. How can I assist you further?"
    
    def process_query(self, user_input: str) -> dict:
        """
        Complete pipeline: Input → Predict Intent → RL Action → Generate Response
        """
        logger.info("=" * 60)
        logger.info(f"User Input: {user_input}")
        logger.info("=" * 60)
        
        # Step 1: Predict intent
        intent, confidence = self.predict_intent(user_input)
        logger.info(f"\n📍 NLP Intent Classification:")
        logger.info(f"   Intent: {intent}")
        logger.info(f"   Confidence: {confidence:.1%}")
        
        # Step 2: Select RL action
        action, q_value = self.select_action(intent)
        logger.info(f"\n🤖 RL Action Selection:")
        logger.info(f"   Action: {action}")
        logger.info(f"   Q-Value: {q_value:.4f}")
        
        # Step 3: Generate response
        response = self.generate_response(intent, action)
        logger.info(f"\n💬 System Response:")
        logger.info(f"   {response}")
        
        # Get all Q-values for this intent
        intent_idx = self.dataset.intent_to_idx[intent]
        q_values = {}
        for action_id, action_name in enumerate(self.rl_agent.ACTIONS):
            q_values[action_name] = float(self.rl_agent.q_table[intent_idx, action_id])
        
        return {
            "user_input": user_input,
            "intent": intent,
            "intent_confidence": confidence,
            "selected_action": action,
            "action_q_value": q_value,
            "all_q_values": q_values,
            "response": response
        }


def main():
    """Interactive demo loop"""
    print("\n" + "=" * 60)
    print("👋 Welcome to Helpify AI - Interactive Demo")
    print("=" * 60)
    print("\nThis demo shows the complete AI system:")
    print("  1. NLP Intent Classification (Text-CNN)")
    print("  2. RL Action Selection (Q-Learning)")
    print("  3. Response Generation")
    print("\nSupported intents:")
    print("  • greeting")
    print("  • order_status")
    print("  • refund_request")
    print("  • complaint")
    print("  • product_inquiry")
    print("  • cancel_order")
    print("  • shipping_issue")
    print("  • account_issue")
    print("\nType 'quit' to exit")
    print("=" * 60 + "\n")
    
    demo = HelpifyAIDemo()
    
    # Example queries
    examples = [
        "I want a refund for my order",
        "Where is my order #12345?",
        "Hello!",
        "Your service is terrible",
        "Can you tell me about your products?",
        "I want to cancel my order",
        "My package hasn't arrived yet",
        "I can't log into my account"
    ]
    
    while True:
        print("\n" + "-" * 60)
        print("Enter a customer support query (or 'examples' for suggestions):")
        user_input = input("> ").strip()
        
        if user_input.lower() == "quit":
            print("\n👋 Goodbye!")
            break
        elif user_input.lower() == "examples":
            print("\nExample queries:")
            for i, ex in enumerate(examples, 1):
                print(f"  {i}. {ex}")
            continue
        elif not user_input:
            print("Please enter a query.")
            continue
        
        result = demo.process_query(user_input)
        
        # Print summary
        print("\n" + "─" * 60)
        print("SUMMARY:")
        print(f"  Intent: {result['intent']} ({result['intent_confidence']:.1%})")
        print(f"  Action: {result['selected_action']}")
        print(f"  Response: {result['response']}")


if __name__ == "__main__":
    main()
