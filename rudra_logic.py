from dotenv import load_dotenv
import logging
import os
import time
from twilio_sms_send import send_sms
from prompts import RUDRA_SYSTEM_PROMPT
from ollama_client import OllamaClientReplacement, CHAT_CONFIG

load_dotenv()

logger = logging.getLogger(__name__)

class RudraAgent:
    def __init__(self, caller_number: str = None, call_sid: str = None, public_url: str = None):
        self.call_transferred = False
        self.is_active = True
        self.has_been_transferred = False  # Once transferred, AI cannot be re-enabled
        self.caller_number = caller_number
        self.call_sid = call_sid
        self.public_url = public_url
        self.location_details = None
        
        # Initialize Ollama client (drop-in replacement for OpenAI)
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma2")
        logger.info(f"🦙 Initializing RudraAgent with Ollama: {base_url} (Model: {model})")
        
        self.client = OllamaClientReplacement(base_url=base_url, model=model)
        self.model_id = model  # Use Ollama model (gemma2 by default)
        
        self.system_prompt = RUDRA_SYSTEM_PROMPT
        
        # Initialize history with system prompt
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Tool markers for Ollama (since native function calling is not supported)
        # We'll prompt the model to use special markers in text responses
        self.tool_markers = {
            "send_location_link": "[TOOL:SEND_LOCATION_LINK]",
            "check_location_status": "[TOOL:CHECK_LOCATION_STATUS]",
        }
        
        # Legacy tools definition (kept for reference, not used with Ollama)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "send_location_link",
                    "description": "Send a link to the caller's phone number to request their live GPS location. Use this IMMEDIATELY to get the caller's location instead of asking verbally.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_location_status",
                    "description": "Check if the caller's location has been received. Use this to verify if the location link has been clicked.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def process_input(self, user_input: str):
        """
        Process user input and return the agent's response using Ollama (Gemma2).
        Returns: (response_text, call_transferred, tool_used)
        """
        # If call has been transferred to human, AI should never respond again
        if self.has_been_transferred or not self.is_active or self.call_transferred:
            return None, True, None

        if not user_input or not user_input.strip():
            return None, False, None

        try:
            # Add user message to history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Generate response with Ollama (note: tools parameter is ignored by Ollama)
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=150,
                tools=self.tools,  # Included for compatibility, but Ollama will ignore this
                tool_choice="auto"  # Included for compatibility, but Ollama will ignore this
            )
            
            message = response.choices[0].message
            response_text = message.content
            
            if not response_text:
                logger.warning("Ollama returned empty response. Sending fallback.")
                fallback_text = "I didn't catch that. Could you please repeat?"
                self.chat_history.append({"role": "assistant", "content": fallback_text})
                return fallback_text, False, None
            
            # Parse tool markers from the response (since Ollama doesn't support native function calling)
            tool_used = None
            
            if "[TOOL:SEND_LOCATION_LINK]" in response_text:
                logger.info(f"🛠️ AI triggered tool: send_location_link for {self.caller_number}")
                tool_used = "send_location_link"
                
                # Execute the tool (send SMS)
                if self.caller_number and self.caller_number != "unknown":
                    base_url = self.public_url if self.public_url else "http://localhost:8000"
                    if base_url.endswith('/'):
                        base_url = base_url[:-1]
                    
                    import uuid
                    request_id = str(uuid.uuid4())[:8]
                    link = f"{base_url}/location-request?id={request_id}&caller={self.caller_number}"
                    sms_body = f"RudraOne Emergency: Please click here to share your live location: {link}"
                    
                    try:
                        send_sms(self.caller_number, sms_body)
                        logger.info(f"✅ Location link SMS sent successfully (request_id: {request_id})")
                    except Exception as e:
                        logger.error(f"❌ Failed to send location SMS: {e}")
                else:
                    logger.warning("⚠️ Cannot send location link: Caller number unknown")
                
                # Clean response by removing tool marker
                tool_response_text = response_text.replace("[TOOL:SEND_LOCATION_LINK]", "").strip()
                if not tool_response_text:
                    tool_response_text = "I have sent a link to your mobile number. Please click on it to share your live location."
                
                self.chat_history.append({"role": "assistant", "content": tool_response_text})
                return tool_response_text, False, tool_used

            elif "[TOOL:CHECK_LOCATION_STATUS]" in response_text:
                logger.info(f"🛠️ AI triggered tool: check_location_status for {self.caller_number}")
                tool_used = "check_location_status"
                
                if self.location_details:
                    tool_response_text = "I have received your location."
                else:
                    tool_response_text = "I haven't received your location yet. Please click the link I sent to your mobile number."
                
                # Clean response by removing tool marker
                tool_response_text = response_text.replace("[TOOL:CHECK_LOCATION_STATUS]", "").strip()
                if not tool_response_text:
                    tool_response_text = "I haven't received your location yet. Please click the link I sent to your mobile number."
                
                self.chat_history.append({"role": "assistant", "content": tool_response_text})
                return tool_response_text, False, tool_used
            
            # Add assistant response to history
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Check if AI wants to transfer the call
            if "TRANSFER_TO_HUMAN:" in response_text:
                self.call_transferred = True
                self.is_active = False
                self.has_been_transferred = True
                parts = response_text.split("TRANSFER_TO_HUMAN:")
                reason = parts[1].strip() if len(parts) > 1 else "emergency situation"
                return f"I'm transferring you to a human dispatcher now. {reason}", True, None
            
            return response_text, self.call_transferred, None
            
        except Exception as e:
            logger.error(f"Error in RudraAgent (Ollama): {e}")
            return "I'm sorry, I'm having trouble processing that. Let me transfer you to a human dispatcher.", True, None

    def process_system_event(self):
        """
        Trigger a response from the agent based on the current history (e.g. after a system update).
        Does NOT add a user message, but generates an assistant response based on the latest state.
        Uses Ollama (Gemma2) for generation.
        Returns: (response_text, call_transferred, tool_used)
        """
        # If call has been transferred to human, AI should never respond again
        if self.has_been_transferred or not self.is_active or self.call_transferred:
            return None, True, None

        try:
            # Generate response with Ollama based on current history (which includes system update)
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=150,
                tools=self.tools,  # Included for compatibility, but Ollama will ignore this
                tool_choice="auto"  # Included for compatibility, but Ollama will ignore this
            )
            
            message = response.choices[0].message
            response_text = message.content
            
            if not response_text:
                return None, False, None

            # Add assistant response to history
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Check if AI wants to transfer the call
            if "TRANSFER_TO_HUMAN:" in response_text:
                self.call_transferred = True
                self.is_active = False
                self.has_been_transferred = True
                parts = response_text.split("TRANSFER_TO_HUMAN:")
                reason = parts[1].strip() if len(parts) > 1 else "emergency situation"
                return response_text.replace(f"TRANSFER_TO_HUMAN: {reason}", f"I'm transferring you to a human dispatcher now. {reason}"), True, None
            
            return response_text, self.call_transferred, None
            
        except Exception as e:
            logger.error(f"Error in RudraAgent (System Event): {e}")
            return None, False, None

    def receive_location_update(self, address: str, language_code: str = "en"):
        """
        Receive location update from the system and inject it into the chat history.
        """
        logger.info(f"📍 RudraAgent received location update: {address} (Language: {language_code})")
        self.location_details = address
        
        lang_map = {
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam"
        }
        language_name = lang_map.get(language_code, "the same language as the caller")
        
        self.chat_history.append({
            "role": "system", 
            "content": f"SYSTEM UPDATE: The caller's live location has been received via the link. Address: {address}. You should acknowledge this to the caller. IMPORTANT: Respond in {language_name} ONLY."
        })


