import os
from cryptography.fernet import Fernet
import json

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Paths
cookie_file = os.path.join(script_dir, "cookies.json")
encrypted_file = os.path.join(script_dir, "encrypted_cookies.bin")
key_file = os.path.join(script_dir, "secret.key")

# Generate a secret key
def generate_key():
    return Fernet.generate_key()

# Encrypt cookies data
def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    return encrypted_data

# Load cookies data from a JSON file
def load_cookies_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return {}  # Return an empty dictionary instead of crashing

    with open(file_path, "r") as file:
        return json.load(file)

# Main encryption function
def encrypt_cookies():
    key = generate_key()
    cookies_data = load_cookies_from_file(cookie_file)

    if not cookies_data:
        print("No cookies to encrypt.")
        return

    encrypted_cookies = encrypt_data(cookies_data, key)

    # Save encrypted data and key
    with open(encrypted_file, "wb") as file:
        file.write(encrypted_cookies)

    with open(key_file, "wb") as keyfile:
        keyfile.write(key)

    print(f"Cookies encrypted successfully!\n- Encrypted file: {encrypted_file}\n- Key file: {key_file}")

# Run encryption
encrypt_cookies()
