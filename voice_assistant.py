import datetime
import os
import time
import pyttsx3
import speech_recognition as sr
from gemini_handler import GeminiHandler

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant with speech recognition and synthesis."""
        self.engine = self.initialize_engine()
        self.recognizer = sr.Recognizer()
        
        # Initialize Gemini LLM handler
        self.gemini = GeminiHandler()
        
        # Set up system prompt for Gemini
        system_prompt = """
        You are JARVIS, an advanced AI assistant similar to the one in Iron Man.
        Your responses should be helpful, concise, and slightly witty when appropriate.
        You should refer to the user as "Sir" or by their name if provided.
        Avoid responses that are too verbose - keep them direct and to the point.
        If you don't know something, admit it rather than making up information.
        """
        self.gemini.set_system_prompt(system_prompt)

    def initialize_engine(self):
        """Initialize the text-to-speech engine."""
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # Use a male voice for JARVIS
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-25)  # Slightly slower than default
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume+0.25)
        return engine

    def speak(self, text):
        """Convert text to speech."""
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for user input through microphone."""
        with sr.Microphone() as source:
            print("Listening...", end="", flush=True)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.recognizer.pause_threshold = 1.0
            self.recognizer.energy_threshold = 4000
            audio = self.recognizer.listen(source)
            
        try:
            print("\rProcessing...", end="", flush=True)
            query = self.recognizer.recognize_google(audio, language='en-in')
            print(f"\rYou said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("\rCouldn't understand audio")
            return ""
        except sr.RequestError:
            print("\rCould not request results from speech recognition service")
            return ""
        except Exception as e:
            print(f"\rError: {str(e)}")
            return ""

    def get_time_greeting(self):
        """Return appropriate greeting based on time of day."""
        hour = datetime.datetime.now().hour
        
        if 0 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 16:
            return "Good afternoon"
        else:
            return "Good evening"

    def wishUser(self, name="Sir"):
        """Greet the user with time-appropriate greeting."""
        greeting = self.get_time_greeting()
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        day = datetime.datetime.now().strftime("%A")
        
        self.speak(f"{greeting}, {name}. It's {day} and the time is {current_time}. How may I assist you today?")

    def process_command(self, command):
        """
        Process user command through Gemini LLM.
        
        Args:
            command (str): The user's voice command
            
        Returns:
            str: The assistant's response
        """
        if not command:
            return "I didn't catch that. Could you please repeat?"
        
        # Get response from Gemini
        response = self.gemini.get_response(command)
        return response

    def run(self, user_name="Sir"):
        """Run the voice assistant in a loop."""
        self.wishUser(user_name)
        
        while True:
            command = self.listen()
            
            # Exit command
            if "goodbye" in command or "bye" in command or "exit" in command or "quit" in command:
                self.speak("Goodbye, Sir. Have a great day.")
                break
                
            # Process the command and get response
            response = self.process_command(command)
            self.speak(response)


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
