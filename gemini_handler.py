import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiHandler:
    def __init__(self):
        """Initialize the Gemini LLM handler."""
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not found. Please set it in the .env file.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Set up the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize conversation history
        self.conversation_history = []
        self.chat_session = self.model.start_chat(history=self.conversation_history)
    
    def get_response(self, user_input):
        """
        Get a response from Gemini LLM.
        
        Args:
            user_input (str): The user's query or command
            
        Returns:
            str: The LLM's response
        """
        try:
            response = self.chat_session.send_message(user_input)
            return response.text
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        self.chat_session = self.model.start_chat(history=self.conversation_history)

    def set_system_prompt(self, system_prompt):
        """
        Set a system prompt to guide the LLM's behavior.
        
        Args:
            system_prompt (str): The system prompt to set
        """
        try:
            # Add system prompt to the conversation
            self.conversation_history = [{"role": "system", "parts": [system_prompt]}]
            self.chat_session = self.model.start_chat(history=self.conversation_history)
            return True
        except Exception as e:
            print(f"Error setting system prompt: {str(e)}")
            return False
