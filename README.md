<div align="center">

# fb_boot - (FB CHATBOT)

A Facebook chatbot powered by the [Google GEMINI-AI API](https://aistudio.google.com/app/apikey).

It utilizes a modified version of `fbchat_muqit` and supports encrypted `cookies.json` for authentication.  
For reference, here is the original version: [fbchat_muqit](https://github.com/togashigreat/fbchat-muqit?tab=BSD-3-Clause-2-ov-file).

⚠️ This is an early release, and several features are still in development. As this is an unofficial API, we are not responsible for any account restrictions or bans imposed by Facebook. We strongly recommend using a dedicated or secondary Facebook account.

</div>

## 🛠️ Documentation
Here's the official fbchat_muqit Docs:
    [Read Documentation](http://fbchat-muqit.rtfd.io/)

## Installation GUIDE:
```bash
#clone the repo
git clone https://github.com/Ion213/fb_boot.git

#open the fb_boot
cd fb_boot

#recommended to create your venv 
python3 -m venv venv
source venv/bin/activate

#change the directory to fbchat-muqit to install the modified fbchat-muqit
cd fbchat-muqit
pip install .

#change back directory to the main
cd ..
#install requirements
pip install -r requirements.txt

#you need to export your gemini api-key
export GENAI_API_KEY="your_api_key"
#Read the guide  below how to encrypt your fb cookies.json
export SECRET_KEY="your_secret_encryption_key"
```

## HOW TO GET YOUR FB cookies:
To log into Facebook, you will need your account cookies, as login via email and password is no longer supported. Follow these steps to obtain your Facebook cookies:

- Log in to your Facebook account.
- Install the [C3C extension](https://github.com/c3cbot/c3c-ufc-utility) in your browser.
- Return to your Facebook account and use the extension while on the Facebook site.
- The extension will generate your cookies, which should be saved in a JSON file.
- These cookies will be used to interact with the Facebook server.

Make sure to store the cookies securely, as they are necessary for accessing Facebook programmatically.


## HOW TO ENCRYPT YOUR FB cookies.json:
Put your fb cookies generated by [C3C extension](https://github.com/c3cbot/c3c-ufc-utility) in the '/key/cookies.json' directory then execute the command below:
```bash
#source venv/bin/activate required
source encrypt.sh #It will create encrypted_cookies.bin and secret_key.key

#⚠️ after encryption, move your original cookies.json and generated secret key in a secured PATH 
#only the encrypted_cookies.bin remains in the /key folder
```
⚠️ Note: After encryption, make sure to store your 'secret_key' and 'cookies.json' in a secure location. Ensure that the path where these files are kept is not publicly accessible, especially if you're deploying on a hosting server. This will help prevent unauthorized access and keep your sensitive data safe.

## RUN THE APP:
```python
#source venv/bin/activate required
python3 app.py
```

## Requirements:
- google-generativeai
- python-dotenv
- cryptography
- fbchat-muqit

### License:

This project is distributed under a dual-license model:

- **BSD-3-Clause License**: Parts of the code are reused and adapted from the original [fbchat](https://github.com/fbchat-dev/fbchat) library, licensed under the BSD-3-Clause License. 
  See [LICENSE-BSD](./LICENSE-BSD.md) for details.

- **GPL v3 License**: New contributions and modifications by Muhammad MuQiT/togashigreat are licensed under the GPL v3.0 License.
See [LICENSE](./LICENSE.md) for details.

