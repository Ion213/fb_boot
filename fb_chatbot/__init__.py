import os
import time

from fbchat_muqit import Client, Message, ThreadType

import google.generativeai as genai
from dotenv import load_dotenv


# Importing functions commands,rules,ai_chat_handling
from .rules.filter_message import filter_messages
from .rules.filter_spam import filter_spams
from .commands.emoji import change_emoji
from .commands.add import add_user
from .commands.remove import remove_user
from .commands.name import change_group_name
from .ai_chat_handling.ai_chat import ai_chats

# Configure Gemini AI API Key
# Load environment variables from .env file
load_dotenv()

# Access the API key from the environment variable
api_key = os.getenv("GENAI_API_KEY")
secret_key = os.getenv("SECRET_KEY")
    
# Configure the AI model with the API key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

class Chat(Client):
    blocked_words = [
        "porn", "sex", "bold", "fuck", "hentai", "pornhub"
    ]  # List of blocked words
    warning_cooldown = {}
    spam_cooldown = {}  # Tracks cooldown for spam message checks
    spam_counts = {}  # Tracks how many times a user has sent the same message
    spam_history = {}  # Tracks the last message and time it was sent
    chat_history = {}  # Stores chat history per user in each thread

    async def onMessage(self, mid, author_id: str, message_object: Message, thread_id, thread_type=ThreadType.USER, **kwargs):
        """Handles incoming messages"""
        if author_id != self.uid:  # Ignore bot's own messages

            user_message = message_object.text.strip()  # Get and clean user's message
            current_time = time.time()

            # Filter bad words
            if await filter_messages(self, mid, author_id, user_message, thread_id, thread_type, current_time):
                return

            # Filter spam messages
            if await filter_spams(self, mid, author_id, user_message, thread_id, thread_type, current_time):
                return

            # Handle emoji change command
            if user_message.startswith("/emoji"):
                await change_emoji(self, author_id, user_message, thread_id, thread_type)
                return

            # Handle add user command
            if user_message.startswith("/add"):
                await add_user(self, author_id, user_message, thread_id, thread_type)
                return

            # Handle remove user command
            if user_message.startswith("/remove"):
                await remove_user(self, author_id, user_message, thread_id, thread_type)
                return

            # Handle change group name command
            if user_message.startswith("/name"):
                await change_group_name(self, author_id, user_message, thread_id, thread_type)
                return

            # Handle AI chat if the message starts with "."
            if user_message.startswith("."):
                await ai_chats(self, author_id, user_message, thread_id, thread_type, message_object, model)
                return
