import json
import random
import os
import logging
from ollama_client import OllamaClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class UnifiedChatSession:
    def __init__(self, ollama_client: OllamaClient):
        """Initialize a chat session with Ollama"""
        self.ollama = ollama_client
        self.history = []  # Maintain conversation history for multi-turn
    
    def send_message(self, message: str) -> 'UnifiedResponse':
        """Send a message and get a response from Ollama"""
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Get response from Ollama
        response_text = self.ollama.chat(
            messages=self.history,
            temperature=0.7,
            max_tokens=512
        )
        
        # Add assistant response to history
        self.history.append({"role": "assistant", "content": response_text})
        
        return UnifiedResponse(response_text)


class UnifiedResponse:
    """Wrapper for Ollama responses to maintain API compatibility"""
    def __init__(self, text):
        self.text = text


class UnifiedTrainingClient:
    """Unified training client that uses Ollama"""
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.chats = self  # Mocking the structure client.chats.create
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma2")
        
        logger.info(f"🦙 Initializing Unified Training Client with Ollama: {base_url} (Model: {model})")
        self.ollama_client = OllamaClient(base_url=base_url, model=model)

    def create(self, model=None):
        """Create a new chat session"""
        return UnifiedChatSession(self.ollama_client)


# Initialize default client for CLI usage
try:
    logger.info("Initializing default training client with Ollama...")
    client = UnifiedTrainingClient()
except Exception as e:
    logger.warning(f"Could not initialize default training client: {e}")
    client = None


def load_scenarios(file_path="911_calls.json"):
    """Load 911 dataset from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def select_random_scenario(scenarios):
    """Select a random call scenario from dataset."""
    scenario = random.choice(scenarios)
    return scenario

def start_training_session(scenario):
    """Initialize chat model for simulated emergency call."""
    title = scenario.get("title", "Unknown Emergency")
    desc = scenario.get("desc", "No description")
    location = scenario.get("twp", "Unknown Location")

    intro_prompt = f"""
You are simulating an emergency call for a 911 dispatcher training. Your role is to be the CALLER.

**CRITICAL INSTRUCTIONS FOR YOUR ROLE:**
1.  **NO DESCRIPTIVE ACTIONS:** Do NOT use parentheses or asterisks to describe sounds, actions, or emotions (e.g., no `(sobbing)`, `*sirens wail*`, `(gasping)`).
2.  **STRAIGHT CONVERSATION ONLY:** Your responses must only contain the words spoken by the caller. It should be a direct, back-and-forth conversation.
3.  **BE A DESCRIPTIVE REPORTER:** Act as a person urgently reporting an emergency. When you answer, provide relevant details about what you see, hear, and know. Your goal is to paint a clear picture of the scene with your words.
4.  **ELABORATE WHEN ASKED:** Start with an urgent opening line. When the dispatcher asks a question, answer it fully. For example, if they ask for the location, don't just say "the train tracks." Say something like, "It's under the train tracks on Maple Avenue, just past the old factory." Provide the important details you have.

**SCENARIO BRIEFING:**
*   **INCIDENT TYPE:** {title}
*   **DESCRIPTION:** {desc}
*   **LOCATION:** {location}

Begin the call now with your opening line. It should be urgent and give a key detail about the emergency.
    """

    if not client:
        print("Error: Training client not initialized. Check your API keys and .env configuration.")
        return

    chat = client.chats.create()
    print("Starting simulated emergency call training...")
    print("Type your dispatcher responses. Type 'end session' to stop.\n")

    response = chat.send_message(intro_prompt)
    print("Caller:", response.text)

    while True:
        dispatcher_input = input("You (Dispatcher): ")
        if dispatcher_input.lower().strip() == "end session":
            grading_prompt = """
Evaluate the trainee’s overall performance in this conversation. 
Provide:
1. A percentage score (0–100%)
2. A brief evaluation of performance (e.g., clarity, calmness, accuracy, empathy).
            """
            eval_response = chat.send_message(grading_prompt)
            print("\n----- SESSION SUMMARY -----")
            print(eval_response.text)
            break

        response = chat.send_message(dispatcher_input)
        print("\nCaller:", response.text)

def main():
    scenarios = load_scenarios("911_calls.json")
    selected = select_random_scenario(scenarios)
    start_training_session(selected)

if __name__ == "__main__":
    main()
