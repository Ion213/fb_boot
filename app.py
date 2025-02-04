#original cannot use the cookies.json in list or array 

'''
import asyncio
from fb_chatbot import Chat  # Import your bot class
import os


async def run_bot():
    """Starts the bot session and listens for messages."""
    current_directory = os.path.dirname(os.path.realpath(__file__))  # Get the current directory of the script
    cookies_path = os.path.join(current_directory, "key", "cookies.json")  # Join it with the 'key' folder and the filename

    # Start the session with the provided cookies
    bot = await Chat.startSession(cookies_path)

    if await bot.isLoggedIn():
        print("Logged in successfully")

    try:
        # Listen for incoming messages
        await bot.listen()
    except Exception as e:
        print("Error:", e)

# Run the bot
if __name__ == "__main__":
    asyncio.run(run_bot())

'''


import asyncio
from fb_chatbot import Chat,secret_key,api_key  # Import your bot class
import os
from cryptography.fernet import Fernet
import json

# Decrypt the encrypted cookies
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())

# Load the encrypted cookies from a file
def load_encrypted_cookies(file_path):
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    return encrypted_data

async def run_bot():
    """Starts the bot session and listens for messages."""
    current_directory = os.path.dirname(os.path.realpath(__file__))  # Get the current directory of the script

    # Path to the encrypted cookies
    encrypted_cookies_path = os.path.join("key", "encrypted_cookies.bin")

    # Retrieve the secret key from environment variables
    
    
    if not secret_key:
        print("Error: SECRET_KEY environment variable is not set.")
        return
    
    if not api_key:
        print("Error: GENAI_API_KEY environment variable is not set.")
        return

    try:
        # Validate the key length
        if len(secret_key) != 44:  # Fernet keys are always 44 characters in base64 format
            raise ValueError("Invalid key length. Please ensure the correct key is set in the environment variable.")

        # Load and decrypt cookies
        encrypted_cookies = load_encrypted_cookies(encrypted_cookies_path)
        cookies_data = decrypt_data(encrypted_cookies, secret_key)  # Pass key directly

        # Convert cookies to dictionary format expected by the bot
        cookies_dict = {cookie['key']: cookie['value'] for cookie in cookies_data}

        # Start the session with the decrypted cookies
        bot = await Chat.startSession(cookies_dict)

        if await bot.isLoggedIn():
            print("Logged in successfully")

        try:
            # Listen for incoming messages
            await bot.listen()
        except Exception as e:
            print("Error:", e)

    except Exception as e:
        print(f"Error: {e}")

# Run the bot
if __name__ == "__main__":
    asyncio.run(run_bot())

