import os
import time

import re
import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urlparse


from fbchat_muqit import Client, Message, ThreadType,FileAttachment

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



#---------------y2mate------------------

# Use random device user to avoid detection
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Linux; Android 4.4.4; Nexus 5 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.135 Mobile Safari/537.36"
]

# Function to get a random User-Agent
def get_random_user_agent():
    return random.choice(user_agents)

# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    parsed_url = urlparse(url)
    if "shorts" in parsed_url.path:
        return parsed_url.path.split('/')[-1]  # Extracting video ID from path
    return None

# Function to extract cookies and CSRF token from the website
def extract_cookies_and_csrf():
    url = "https://en.y2mate.is/x107/"  # The URL where cookies and CSRF token are set
    headers = {
        "User-Agent": get_random_user_agent()
    }
    
    # Perform GET request to extract cookies and CSRF token
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Extract the CSRF token from the page content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = None
        
        # Look for the CSRF token in meta tags or hidden inputs
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            csrf_token = csrf_meta.get('content')
        
        # Extract cookies from the response
        cookies = response.cookies
        
        return cookies, csrf_token
    else:
        print("Failed to retrieve cookies or CSRF token.")
        return None, None

#----------------y2mate------------------

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


            # Check if the message contains a YouTube Shorts link
            youtube_match = re.search(r"(https?://(?:www\.)?youtube\.com/shorts/\S+)", user_message)
            if youtube_match:
                youtube_url = youtube_match.group(0)
                video_id = extract_video_id(youtube_url)

                if video_id:
                    # Extract cookies and CSRF token
                    cookies, csrf_token = extract_cookies_and_csrf()
                    
                    if cookies and csrf_token:
                        # The data for the request with the extracted video ID and URL
                        data = {
                            "id": video_id,  # Video ID
                            "url": youtube_url,  # Full URL
                            "format": "mp4"
                        }

                        # Headers for the request
                        headers = {
                            "Accept": "*/*",
                            "Accept-Encoding": "gzip, deflate, br, zstd",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Connection": "keep-alive",
                            "Content-Type": "application/json",
                            "Host": "en.y2mate.is",
                            "Origin": "https://en.y2mate.is",
                            "Referer": "https://en.y2mate.is/x107/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "User-Agent": get_random_user_agent(),
                            "X-CSRF-TOKEN": csrf_token,  # Include the CSRF token in the headers
                        }

                        # Sending the POST request with the extracted cookies and CSRF token
                        response = requests.post("https://en.y2mate.is/getconvert", json=data, headers=headers, cookies=cookies)

                        # Checking the response
                        if response.status_code == 200:
                            try:
                                response_json = response.json()  # Try parsing as JSON
                                download_link = response_json.get("download")  # Get the download link using the correct key
                                if download_link:
                                    # Send the video download link
                                    await self.sendRemoteFiles(
                                        file_urls=[download_link],
                                        message="🎥 Here's your video!",
                                        thread_id=thread_id,
                                        thread_type=thread_type
                                    )
                                else:
                                    await self.send(Message(text="❌ Failed to get download link."), thread_id=thread_id, thread_type=thread_type)
                            except ValueError as e:
                                print("Error parsing the response:", str(e))
                                await self.send(Message(text="❌ Failed to process the response."), thread_id=thread_id, thread_type=thread_type)
                        else:
                            print(f"Request failed with status code {response.status_code}")
                            await self.send(Message(text="❌ Failed to fetch video details."), thread_id=thread_id, thread_type=thread_type)
                    else:
                        await self.send(Message(text="❌ Failed to extract cookies or CSRF token."), thread_id=thread_id, thread_type=thread_type)
                else:
                    await self.send(Message(text="❌ Failed to extract video ID."), thread_id=thread_id, thread_type=thread_type)
                return  # Stop processing further
            