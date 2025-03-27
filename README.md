# JARVIS - Voice Assistant with Gemini LLM

A voice-controlled AI assistant inspired by Iron Man's JARVIS, powered by Google's Gemini LLM for advanced conversational capabilities.

## Features

- **Voice Recognition**: Listens to and processes voice commands
- **Text-to-Speech**: Responds with natural-sounding speech
- **Intent Classification**: Uses a trained neural network model to classify user intents
- **Gemini LLM Integration**: Leverages Google's Gemini LLM for advanced conversational abilities
- **System Controls**: Control volume, open/close applications, and more
- **Web Browsing**: Open websites and perform searches
- **System Monitoring**: Check system conditions like battery and CPU usage

## Setup Instructions

1. **Clone the repository**

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Set up Gemini API key**
   - Rename `.env.example` to `.env`
   - Add your Gemini API key to the `.env` file
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   - You can get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **Run the assistant**
   ```
   python main.py
   ```
   or
   ```
   python voice_assistant.py
   ```

## Usage

- The assistant will greet you upon startup
- Speak commands clearly into your microphone
- Say "goodbye", "bye", "exit", or "quit" to exit the program

## Available Commands

- **Social Media**: "Open Facebook/WhatsApp/Discord/Instagram"
- **Schedule**: "What's my schedule today?" or "University timetable"
- **Volume Control**: "Volume up/down/mute"
- **Applications**: "Open/close calculator/notepad/paint"
- **Web Browsing**: "Google search"
- **System Info**: "System condition"
- **General Conversation**: Ask any question to engage with the Gemini LLM

## Project Structure

- `main.py`: Main application with combined functionality
- `voice_assistant.py`: Standalone voice assistant with Gemini integration
- `gemini_handler.py`: Handles interactions with the Gemini LLM
- `model_train.py`: Script to train the intent classification model
- `model_test.py`: Script to test the intent classification model
- `intents.json`: Contains training data for intent classification

## Customization

- Modify `intents.json` to add new intents and training phrases
- Run `model_train.py` to retrain the model after modifying intents
- Adjust the system prompt in `gemini_handler.py` to change the assistant's personality

## Requirements

- Python 3.8+
- Working microphone and speakers
- Internet connection for speech recognition and Gemini API
- Gemini API key
