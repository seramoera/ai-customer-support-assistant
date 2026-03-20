# Simple NLP intent classifier scaffold
class IntentClassifier:
    def __init__(self, intents=['greeting', 'complaint', 'info']):
        self.intents = intents

    def predict(self, text):
        # Currently a stub: returns 'info' for all
        return 'info'

# Example usage
classifier = IntentClassifier()
sample_text = "Hello, I need help with my account"
predicted_intent = classifier.predict(sample_text)
print(f"Text: {sample_text}")
print(f"Predicted Intent: {predicted_intent}")
