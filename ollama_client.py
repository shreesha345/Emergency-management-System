"""
Ollama Client Wrapper for RudraOne
Provides unified interface to Ollama models (Gemma, Mistral, etc.)
Replaces OpenAI, Google Gemini, and other cloud-based LLM providers
"""
import os
import json
import logging
import httpx
import asyncio
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Check if Ollama is enabled
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() in ("true", "1", "yes")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:31b")


class OllamaClient:
    """
    Wrapper for Ollama API with fallbacks and error handling.
    Can be enabled/disabled via OLLAMA_ENABLED environment variable.
    """

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = 300,
        enabled: bool = None,
    ):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model: Model name to use (default: gemma4:31b)
            timeout: Request timeout in seconds
            enabled: Whether Ollama is enabled (default: from OLLAMA_ENABLED env var)
        """
        # Use provided enabled status or fall back to environment variable
        self.enabled = enabled if enabled is not None else OLLAMA_ENABLED
        
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.timeout = timeout
        
        # Ensure base_url doesn't have trailing slash
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        self.api_endpoint = f"{self.base_url}/api"
        
        status = "✅ ENABLED" if self.enabled else "⚠️ DISABLED"
        logger.info(f"🦙 Ollama Client initialized: {status}")
        logger.info(f"   URL: {self.base_url}, Model: {self.model}")
        
        
    def _check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = httpx.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Cannot connect to Ollama at {self.base_url}: {e}")
            return False
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send chat message to Ollama and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length (optional)
            **kwargs: Additional parameters
        
        Returns:
            Response text from the model
        """
        if not self.enabled:
            logger.warning("⚠️ Ollama is disabled. Returning fallback response.")
            return self._get_fallback_response(messages)
        
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False,
            }
            
            # Add optional parameters
            if max_tokens:
                payload["num_predict"] = max_tokens
            
            # Make request to Ollama
            response = httpx.post(
                f"{self.api_endpoint}/chat",
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API returned {response.status_code}")
            
            result = response.json()
            content = result.get("message", {}).get("content", "")
            
            logger.debug(f"✅ Ollama chat response received ({len(content)} chars)")
            return content
            
        except httpx.ConnectError:
            logger.error(f"❌ Cannot connect to Ollama at {self.base_url}")
            raise Exception(f"Ollama server not running at {self.base_url}")
        except Exception as e:
            logger.error(f"❌ Ollama chat error: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            max_tokens: Maximum response length
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        if not self.enabled:
            logger.warning("⚠️ Ollama is disabled. Returning fallback response.")
            return self._get_fallback_response([{"role": "user", "content": prompt}])
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
            }
            
            if max_tokens:
                payload["num_predict"] = max_tokens
            
            response = httpx.post(
                f"{self.api_endpoint}/generate",
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                raise Exception(f"Ollama API returned {response.status_code}")
            
            result = response.json()
            generated_text = result.get("response", "")
            
            logger.debug(f"✅ Ollama generate response received ({len(generated_text)} chars)")
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Ollama generate error: {e}")
            raise
    
    def _get_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Return a fallback response when Ollama is disabled or unavailable.
        Extracts last user message for context.
        
        Args:
            messages: List of messages
        
        Returns:
            Generic fallback response
        """
        # Get the last user message for context
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        # Return contextual fallback responses
        if not last_user_msg:
            return "I'm unable to process your request at this time. Ollama is disabled."
        
        # Some intelligent fallback based on context
        lower_msg = last_user_msg.lower()
        
        if any(word in lower_msg for word in ["emergency", "fire", "accident", "medical"]):
            return "Emergency dispatch system is currently unavailable. Please contact emergency services directly at 911 or your local emergency number."
        elif any(word in lower_msg for word in ["sms", "message", "send"]):
            return "SMS formatting service is currently unavailable."
        elif any(word in lower_msg for word in ["analytics", "chart", "data", "statistics"]):
            return "Analytics system is currently unavailable. Please contact your administrator."
        elif any(word in lower_msg for word in ["train", "learning", "session"]):
            return "Training system is currently unavailable."
        else:
            return "The AI system is currently disabled. Please enable Ollama to use this feature."
    
    def pull_model(self, model_name: str = None) -> bool:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of model to pull (default: self.model)
        
        Returns:
            True if successful
        """
        model_to_pull = model_name or self.model
        logger.info(f"🔄 Pulling model: {model_to_pull}...")
        
        try:
            payload = {"name": model_to_pull}
            response = httpx.post(
                f"{self.api_endpoint}/pull",
                json=payload,
                timeout=600,  # Long timeout for pulling
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Model {model_to_pull} pulled successfully")
                return True
            else:
                logger.error(f"❌ Failed to pull model: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Pull model error: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List all available models on Ollama server
        
        Returns:
            List of model names
        """
        try:
            response = httpx.get(
                f"{self.api_endpoint}/tags",
                timeout=10,
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Cannot list models: {response.status_code}")
                return []
            
            result = response.json()
            models = [m.get("name", "") for m in result.get("models", [])]
            logger.info(f"📦 Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"❌ List models error: {e}")
            return []


class OllamaChatCompletion:
    """
    OpenAI-compatible chat completion interface for Ollama.
    Allows drop-in replacement of OpenAI client in existing code.
    """
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
    
    def create(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = None,
        tools: List[Dict] = None,
        tool_choice: str = None,
        **kwargs
    ):
        """
        OpenAI-compatible chat completion method
        
        Args:
            model: Model name (ignored, uses Ollama client's model)
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            tools: Function definitions (not supported in Ollama, logged)
            tool_choice: Tool selection strategy (not supported, logged)
            **kwargs: Additional parameters
        
        Returns:
            Response object compatible with OpenAI format
        """
        if tools:
            logger.warning("⚠️ Function calling/tools not supported in Ollama (gemma4:31b)")
            logger.warning("   Continuing without tools...")
        
        if tool_choice:
            logger.warning("⚠️ tool_choice parameter ignored in Ollama")
        
        # Get response from Ollama
        content = self.ollama.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Return OpenAI-compatible response object
        return OllamaCompletionResponse(content, model or self.ollama.model)


class OllamaCompletionResponse:
    """OpenAI-compatible completion response object"""
    
    def __init__(self, content: str, model: str):
        self.content = content
        self.model = model
        self.message = OllamaMessage(content, self.model)
        self.choices = [OllamaChoice(content, self.model)]


class OllamaChoice:
    """OpenAI-compatible choice object"""
    
    def __init__(self, content: str, model: str):
        self.message = OllamaMessage(content, model)
        self.finish_reason = "stop"


class OllamaMessage:
    """OpenAI-compatible message object"""
    
    def __init__(self, content: str, model: str):
        self.content = content
        self.role = "assistant"
        self.tool_calls = None  # Not supported in this setup


# Convenience function to create a drop-in replacement for OpenAI client
def create_ollama_replacement(
    base_url: str = None,
    model: str = None,
) -> 'OllamaClientReplacement':
    """
    Create an Ollama client that mimics OpenAI.Client interface
    
    Args:
        base_url: Ollama server URL
        model: Model to use
    
    Returns:
        Client object with .chat.completions.create() method
    """
    return OllamaClientReplacement(base_url=base_url, model=model)


class OllamaClientReplacement:
    """Drop-in replacement for OpenAI.Client"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.ollama = OllamaClient(base_url=base_url, model=model)
        self.chat = OllamaChat(self.ollama)


class OllamaChat:
    """Mimics OpenAI.client.chat interface"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.completions = OllamaChatCompletion(ollama_client)


# Configuration preset for Gemma 4
GEMMA4_CONFIG = {
    "model": "gemma4:31b",
    "temperature": 0.7,
    "max_tokens": 512,
}

# Configuration preset for conversational AI
CHAT_CONFIG = {
    "model": "gemma4:31b",
    "temperature": 0.7,
    "max_tokens": 150,
}

# Configuration preset for analytics (deterministic)
ANALYTICS_CONFIG = {
    "model": "gemma4:31b",
    "temperature": 0.0,
    "max_tokens": 500,
}

# Configuration preset for text generation
GENERATION_CONFIG = {
    "model": "gemma4:31b",
    "temperature": 0.5,
    "max_tokens": 256,
}
