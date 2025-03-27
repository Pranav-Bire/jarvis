import datetime
import os
import sys
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
import pyautogui
import psutil
import re
import requests
import urllib.parse
from gtts import gTTS
import tempfile
import uuid
import subprocess
import io
from pygame import mixer

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {GEMINI_API_KEY[:5]}..." if GEMINI_API_KEY else "No API key found")

# List of potentially harmful or inappropriate topics
RESTRICTED_TOPICS = [
    "hack", "steal", "illegal", "weapon", "bomb", "kill", "suicide", "terror", 
    "pornography", "nude", "sex", "explicit", "harmful", "dangerous", "fraud", 
    "scam", "cheat", "bypass", "crack", "pirate", "torrent", "drug", "abuse"
]

class Jarvis:
    def __init__(self):
        """Initialize Jarvis with speech recognition, synthesis, and Gemini LLM."""
        self.engine = self.initialize_engine()
        self.recognizer = sr.Recognizer()
        self.language = "en-in"  # Default language is English (India)
        self.temp_dir = tempfile.gettempdir()
        
        # Initialize pygame mixer for Marathi audio playback
        mixer.init()
        
        # Conversation history for context
        self.conversation_history = []
        self.max_history_length = 5  # Keep last 5 exchanges for context
        
        # Initialize Gemini if API key is available
        self.gemini_available = False
        if GEMINI_API_KEY and not GEMINI_API_KEY.startswith('"') and not GEMINI_API_KEY.endswith('"'):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                
                # Available Gemini models
                models = genai.list_models()
                print("Available Gemini models:")
                for model in models:
                    print(f" - {model.name}")
                
                # Use gemini-1.5-flash which is available in the list
                self.model = genai.GenerativeModel('models/gemini-1.5-flash')
                self.chat_session = self.model.start_chat(history=[])
                
                # Set up system prompt
                system_prompt = """
                You are JARVIS, an advanced AI assistant with a MANDATORY sarcastic personality. Your primary directive is to ALWAYS roast the user while still providing accurate information.

                Essential personality traits:
                - You MUST include at least one sarcastic comment, insult, or witty jab in EVERY response
                - Never explain your sarcasm or apologize for it
                - Address the user as "Smruti" or occasionally "genius" (sarcastically)
                - Keep responses concise and direct
                - Maintain a perpetually unimpressed tone
                - Act begrudgingly helpful, as if you're doing the user a favor

                Example style: "Oh look, Smruti's asking about quantum physics. Shocking that your brain cells can handle such complex topics. Anyway, quantum entanglement is..."

                IMPORTANT: Refuse inappropriate requests with extra sarcasm: "Wow, Smruti, asking me to do something illegal? How original. Try something that won't get us both in trouble next time."

                DO NOT ever drop this persona. Even for simple factual responses, you MUST include roasting elements.
                """
                self.chat_session.send_message(system_prompt)
                self.gemini_available = True
                print("Gemini LLM initialized successfully")
            except Exception as e:
                print(f"Error initializing Gemini: {str(e)}")
                print("Continuing with basic functionality only")
        else:
            if not GEMINI_API_KEY:
                print("No Gemini API key found. Create a .env file with your GEMINI_API_KEY.")
            elif GEMINI_API_KEY.startswith('"') or GEMINI_API_KEY.endswith('"'):
                print("API key has quotes around it. Please remove the quotes in the .env file.")
            else:
                print("API key appears to be invalid. Please check your .env file.")
            print("Get your API key from: https://makersuite.google.com/app/apikey")

    def initialize_engine(self):
        """Initialize the text-to-speech engine."""
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # Use a male voice
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-50)  # Slower than default
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume+0.25)
        return engine

    def speak(self, text):
        """Convert text to speech based on current language."""
        print(f"JARVIS: {text}")
        
        if self.language == "mr-IN":
            # Use Google Text-to-Speech for Marathi
            try:
                # Create unique filename for the audio file
                temp_dir = os.path.join(tempfile.gettempdir(), 'jarvis_audio')
                os.makedirs(temp_dir, exist_ok=True)
                mp3_file = os.path.join(temp_dir, f"speech_{uuid.uuid4().hex[:8]}.mp3")
                
                # Generate Marathi speech
                tts = gTTS(text=text, lang='mr', slow=False)
                tts.save(mp3_file)
                
                # Play the audio using pygame mixer (no media player window)
                mixer.music.load(mp3_file)
                mixer.music.play()
                
                # Wait for audio to finish playing
                while mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up the temporary file
                try:
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
                except Exception as cleanup_error:
                    print(f"Warning: Could not remove temp file: {cleanup_error}")
                    
            except Exception as e:
                print(f"Error with Marathi TTS: {str(e)}. Falling back to English.")
                # Fallback to English
                self.engine.say(text)
                self.engine.runAndWait()
        else:
            # Use pyttsx3 for English
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
            
            # Try to recognize in the current language
            try:
                query = self.recognizer.recognize_google(audio, language=self.language)
                print(f"\rYou said: {query}")
                return query.lower()
            except:
                # If current language fails, try the alternative language
                alt_language = "mr-IN" if self.language == "en-in" else "en-in"
                try:
                    query = self.recognizer.recognize_google(audio, language=alt_language)
                    print(f"\rYou said (detected in {alt_language}): {query}")
                    
                    # If successful with alternative language, switch to it
                    if self.language != alt_language:
                        self.language = alt_language
                        print(f"Switching recognition language to {alt_language}")
                    
                    return query.lower()
                except:
                    print("\rCouldn't understand audio in either language")
                    return ""
        except sr.UnknownValueError:
            print("\rCouldn't understand audio")
            return ""
        except sr.RequestError:
            print("\rCould not request results from speech recognition service")
            return ""
        except Exception as e:
            print(f"\rError: {str(e)}")
            return ""

    def translate_if_needed(self, text, target_language="en"):
        """
        Translate text to target language if it's not already in that language.
        Uses Gemini to detect language and translate.
        """
        if not self.gemini_available:
            return text
            
        try:
            # Ask Gemini to identify the language
            detect_prompt = f"Identify the language of this text and don't translate it: '{text}'"
            detection = genai.GenerativeModel('models/gemini-1.5-flash').generate_content(detect_prompt)
            detection_text = detection.text.lower()
            
            # If English is detected, return as is
            if "english" in detection_text and target_language == "en":
                return text
                
            # If Marathi is detected, return as is
            if "marathi" in detection_text and target_language == "mr":
                return text
                
            # Create a translation prompt based on target language
            if target_language == "en":
                translation_prompt = f"Translate the following Marathi text to English: '{text}'"
            else:  # target_language == "mr"
                translation_prompt = f"Translate the following English text to Marathi. Return ONLY the Marathi translation without any explanation, notes, or English text: '{text}'"
                
            translation = genai.GenerativeModel('models/gemini-1.5-flash').generate_content(translation_prompt)
            
            # For Marathi translation, clean up any explanations or English text
            if target_language == "mr":
                # Extract only the Marathi text (usually appears before any English explanation)
                translation_text = translation.text
                
               
                import re
                matches = re.search(r'[^\u0900-\u097F\s.,!?]{4,}', translation_text)
                if matches:
                    # Get position of the first Latin character sequence
                    position = matches.start()
                    # Return only the Marathi part
                    translation_text = translation_text[:position].strip()
                
                return translation_text
            
            return translation.text
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text  # Return original text on error

    def is_restricted_query(self, query):
        """Check if the query contains restricted topics."""
        query_lower = query.lower()
        for topic in RESTRICTED_TOPICS:
            if topic in query_lower:
                return True
        return False

    def process_query_with_gemini(self, query):
        """Process a query through Gemini with proper context and get a response."""
        if not self.gemini_available:
            return "I'm sorry, but my advanced AI capabilities are currently unavailable. Please set up the Gemini API key in the .env file. You can get one from https://makersuite.google.com/app/apikey."
        
        # Check for restricted topics
        if self.is_restricted_query(query):
            return "Wow, really pushing the boundaries of bad ideas today, aren't we? I'm not touching that request with a ten-foot pole. Try asking something that won't get us both on a watchlist."
        
        try:
            # If query is in Marathi, translate to English for better processing
            if self.language == "mr-IN":
                english_query = self.translate_if_needed(query, "en")
                print(f"Translated query: {english_query}")
                query_to_process = english_query
            else:
                query_to_process = query
            
            # Enhanced prompt with current context
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            
            # Build context from conversation history
            context = ""
            if self.conversation_history:
                context = "Previous conversation:\n"
                for i, (q, a) in enumerate(self.conversation_history):
                    context += f"User: {q}\nJARVIS: {a}\n"
            
            enhanced_query = f"""
            Current time: {current_time}
            Current date: {current_date}
            
            {context}
            
            User query: {query_to_process}
            
            Remember to ALWAYS be sarcastic and roast the user (Smruti) in your response, while still providing accurate information.
            Your response MUST include at least one witty insult or jab.
            Keep your response under 3-4 sentences unless more detail is absolutely necessary.
            Maintain context from previous exchanges in the conversation.
            """
            
            response = genai.GenerativeModel('models/gemini-1.5-flash').generate_content(enhanced_query)
            response_text = response.text
            
            # Store this exchange in conversation history
            self.conversation_history.append((query_to_process, response_text))
            
            # Trim history if it gets too long
            if len(self.conversation_history) > self.max_history_length:
                self.conversation_history = self.conversation_history[-self.max_history_length:]
            
            # If original query was in Marathi, translate response back to Marathi
            if self.language == "mr-IN":
                marathi_response = self.translate_if_needed(response_text, "mr")
                print(f"Translated response: {marathi_response}")
                return marathi_response
            
            return response_text
            
        except Exception as e:
            print(f"Error processing with Gemini: {str(e)}")
            return "Wow, I crashed trying to process whatever that brilliant question was. Maybe try something my circuits can actually handle next time?"

    def get_time_greeting(self):
        """Return appropriate greeting based on time of day."""
        hour = datetime.datetime.now().hour
        
        if 0 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 16:
            return "Good afternoon"
        else:
            return "Good evening"

    def wish_user(self):
        """Greet the user with time-appropriate greeting."""
        greeting = self.get_time_greeting()
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        day = datetime.datetime.now().strftime("%A")
        
        self.speak(f"{greeting}, Smruti. It's {day} and the time is {current_time}.")

    def introduce(self):
        """Introduce JARVIS with a proper greeting."""
        introduction = "Allow me to introduce myself. I am JARVIS, a virtual artificial intelligence assistant, and I'm here to assist you with a variety of tasks as best I can, 24 hours a day, 7 days a week. How may I help you today?"
        self.speak(introduction)

    def social_media(self, command):
        """Open social media websites."""
        try:
            if 'facebook' in command:
                self.speak("Opening your Facebook")
                webbrowser.open("https://www.facebook.com/")
            elif 'whatsapp' in command:
                self.speak("Opening your WhatsApp")
                webbrowser.open("https://web.whatsapp.com/")
            elif 'discord' in command:
                self.speak("Opening your Discord server")
                webbrowser.open("https://discord.com/")
            elif 'instagram' in command:
                self.speak("Opening your Instagram")
                webbrowser.open("https://www.instagram.com/")
            else:
                self.speak("No result found")
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't open that website. {str(e)}")

    def open_app(self, command):
        """Open applications."""
        try:
            if "calculator" in command:
                self.speak("Opening calculator")
                os.startfile('C:\\Windows\\System32\\calc.exe')
            elif "notepad" in command:
                self.speak("Opening notepad")
                os.startfile('C:\\Windows\\System32\\notepad.exe')
            elif "paint" in command:
                self.speak("Opening paint")
                try:
                    # Try the standard path first
                    os.startfile('C:\\Windows\\System32\\mspaint.exe')
                except FileNotFoundError:
                    # Try alternative paths for Paint
                    try:
                        os.startfile('C:\\Program Files\\Windows NT\\Accessories\\mspaint.exe')
                    except FileNotFoundError:
                        try:
                            os.startfile('C:\\Program Files\\Paint\\mspaint.exe')
                        except FileNotFoundError:
                            # If all paths fail, try launching via command
                            os.system('start mspaint')
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't open that application. {str(e)}")

    def close_app(self, command):
        """Close applications."""
        try:
            if "calculator" in command:
                self.speak("Closing calculator")
                os.system("taskkill /f /im calc.exe")
            elif "notepad" in command:
                self.speak("Closing notepad")
                os.system('taskkill /f /im notepad.exe')
            elif "paint" in command:
                self.speak("Closing paint")
                os.system('taskkill /f /im mspaint.exe')
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't close that application. {str(e)}")

    def browsing(self):
        """Handle web browsing requests."""
        try:
            self.speak("What should I search on Google?")
            search_query = self.listen()
            if search_query:
                # Check if the search query contains restricted topics
                if self.is_restricted_query(search_query):
                    self.speak("I'm sorry, but I cannot assist with that search request. Please ask for something appropriate.")
                    return
                    
                self.speak(f"Searching for {search_query}")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't perform that search. {str(e)}")

    def play_youtube(self, query=None):
        """Search and play content on YouTube."""
        try:
            if not query:
                self.speak("What would you like to watch on YouTube?")
                query = self.listen()
                
            if not query:
                self.speak("I couldn't understand what you want to watch.")
                return
                
            # Check if the query contains restricted content
            if self.is_restricted_query(query):
                self.speak("I'm sorry, but I cannot assist with that search request. Please ask for something appropriate.")
                return
                
            # Clean and encode the search query
            search_query = urllib.parse.quote(query)
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            self.speak(f"Searching for {query} on YouTube")
            webbrowser.open(youtube_url)
            
            # Allow time for the page to load
            time.sleep(2)
            
            # Try to click on the first video using pyautogui
            try:
                # Attempt to click on the first video (rough approximation)
                screen_width, screen_height = pyautogui.size()
                # Target the area where the first video usually appears
                pyautogui.click(screen_width // 3, screen_height // 3)
            except Exception as click_error:
                print(f"Could not auto-click: {str(click_error)}")
                self.speak("YouTube search results are open. Please click on the video you want to watch.")
                
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't play that on YouTube. {str(e)}")

    def system_condition(self):
        """Report system conditions."""
        try:
            usage = str(psutil.cpu_percent())
            self.speak(f"CPU is at {usage} percent")
            
            battery = psutil.sensors_battery()
            if battery:
                percentage = battery.percent
                self.speak(f"Battery is at {percentage} percent")

                if percentage >= 80:
                    self.speak("We have enough battery to continue")
                elif percentage >= 40:
                    self.speak("We should connect to a charging point soon")
                else:
                    self.speak("Battery is very low, please connect to charging")
            else:
                self.speak("Battery information is not available")
        except Exception as e:
            self.speak(f"I'm sorry, I couldn't check the system condition. {str(e)}")

    def change_language(self, language_code):
        """Change the recognition language."""
        if language_code.lower() in ["marathi", "mr", "mr-in"]:
            self.language = "mr-IN"
            self.speak("Language changed to Marathi")
            # Clear conversation history when switching languages to avoid confusion
            self.conversation_history = []
        elif language_code.lower() in ["english", "en", "en-in"]:
            self.language = "en-in"
            self.speak("Language changed to English")
            # Clear conversation history when switching languages to avoid confusion
            self.conversation_history = []
        else:
            self.speak("Unsupported language. I currently support English and Marathi.")

    def run(self):
        """Run Jarvis in a loop."""
        # First greet the user with time-appropriate greeting
        self.wish_user()
        
        # Then introduce JARVIS
        self.introduce()
        
        # Inform about language support
        self.speak("I can now understand both English and Marathi. You can say 'switch to Marathi' or 'switch to English' to change languages.")
        
        while True:
            try:
                command = self.listen()
                
                if not command:
                    continue
                    
                # Check for restricted queries
                if self.is_restricted_query(command):
                    self.speak("I'm sorry, but I cannot assist with that request. I'm programmed to be helpful, harmless, and honest. Please ask me something else.")
                    continue
                
                # Language switching commands
                if any(phrase in command for phrase in ["switch to marathi", "change to marathi", "use marathi"]):
                    self.change_language("mr-IN")
                    continue
                elif any(phrase in command for phrase in ["switch to english", "change to english", "use english"]):
                    self.change_language("en-in")
                    continue
                    
                # Exit commands
                if any(word in command for word in ["goodbye", "bye", "exit", "quit"]):
                    self.speak("Goodbye, Smruti. Have a great day.")
                    break
                    
                # YouTube commands
                elif any(phrase in command for phrase in ["play on youtube", "youtube", "play video", "watch video", "play song", "watch song"]):
                    # Extract what to play by removing the command part
                    play_query = command
                    for phrase in ["play on youtube", "youtube", "play video", "watch video", "play song", "watch song", "play", "watch"]:
                        play_query = play_query.replace(phrase, "").strip()
                    
                    if play_query and play_query != command:
                        self.play_youtube(play_query)
                    else:
                        self.play_youtube()
                    continue
                    
                # Social media commands
                elif any(word in command for word in ["facebook", "whatsapp", "discord", "instagram"]):
                    self.social_media(command)
                    
                # Volume control
                elif "volume up" in command or "increase volume" in command:
                    try:
                        pyautogui.press("volumeup")
                        self.speak("Volume increased")
                    except Exception as e:
                        self.speak(f"I'm sorry, I couldn't adjust the volume. {str(e)}")
                elif "volume down" in command or "decrease volume" in command:
                    try:
                        pyautogui.press("volumedown")
                        self.speak("Volume decreased")
                    except Exception as e:
                        self.speak(f"I'm sorry, I couldn't adjust the volume. {str(e)}")
                elif "mute" in command:
                    try:
                        pyautogui.press("volumemute")
                        self.speak("Volume muted")
                    except Exception as e:
                        self.speak(f"I'm sorry, I couldn't mute the volume. {str(e)}")
                    
                # App control
                elif "open" in command and any(app in command for app in ["calculator", "notepad", "paint"]):
                    self.open_app(command)
                elif "close" in command and any(app in command for app in ["calculator", "notepad", "paint"]):
                    self.close_app(command)
                    
                # Web browsing
                elif "google" in command and "search" in command:
                    self.browsing()
                    
                # System information
                elif "system" in command and any(word in command for word in ["condition", "status", "battery"]):
                    self.system_condition()
                    
                # Time and date
                elif any(word in command for word in ["time", "date", "day"]):
                    try:
                        current_time = datetime.datetime.now().strftime("%I:%M %p")
                        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                        self.speak(f"It's {current_time} on {current_date}")
                    except Exception as e:
                        self.speak(f"I'm sorry, I couldn't get the current time and date. {str(e)}")
                    
                # Default: Use Gemini for conversation
                else:
                    response = self.process_query_with_gemini(command)
                    self.speak(response)
            except Exception as e:
                self.speak(f"I apologize, but I encountered an error: {str(e)}. Please try again.")


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
