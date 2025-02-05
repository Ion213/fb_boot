<div align="center">

# fbchat-muqit Facebook & Messenger API

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fbchat-muqit)
[![fbchat-muqit](https://badgen.net/pypi/v/fbchat-muqit/)](https://pypi.org/project/fbchat-muqit/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**fbchat-muqit** An Unofficial Asynchronous Facebook Messenger API designed to interact with Facebook and Messenger. It is an early release. Most of the feautures are not available yet. 
As It is an Unofficial API we are not responsible if you get banned by Facebook. We recommend to use a dummy Facebook account.

</div>

## 🛠️ Installation

You can install fbchat-muqit using pip:

```bash
pip install fbchat-muqit

```


## 📙 Documentation

The API is not fully documented yet [Read Documentation](http://fbchat-muqit.rtfd.io/)

## 📖 Usage Example

To login in Facebook you will need Facebook account cookies. Since login via email and password is no longer supported. To get your Facebook account cookies. First login in your Facebook account and then add [C3C extension](https://github.com/c3cbot/c3c-ufc-utility) in your browser. Go back to your Facebook account and use this extension while you are on Facebook. You will get the cookies save the cookies in a json file. We will use the cookies to interact with Facebook server.

A basic example of How to use it.

```python
import asyncio
from fbchat_muqit import Client, ThreadType

async def main():
    cookies_path = "path to json cookies"
    # Lets login in Facebook
    bot = await Client.startSession(cookies_path)
    if await bot.isLoggedIn():

        """Lets send a Message to a friend when Client is logged in."""
                                        # put a valid fb user id
        await bot.sendMessage("I'm Online!", "10000072727288", ThreadType.USER)
        print("Logged in as", bot.uid)
    # listen to all incoming events
    await bot.listen()

asyncio.run(main())

```

Subclassing Client class. 

```python

from fbchat_muqit import Client, Message, ThreadType
import asyncio
# Create a class use Client as base Class
class Test(Client):

    async def onMessage(self, mid, author_id: str, message_object: Message, thread_id, thread_type=ThreadType.USER, **kwargs):

        """you will receive all messenger messages here every time anyone sends messages in a thread (Group/User)"""
        # author_id is message sender ID
        if author_id != self.uid:
            await message_object.reply("Hello! This is a reply")
            await message_object.react("❤️")
            # mid is message ID
            await self.sendMessage("Hello", thread_id, thread_type, reply_to_id=mid)


async def main():
    cookies_path = "path to json cookies"
    bot = await Test.startSession(cookies_path)
    if await bot.isLoggedIn():
        fetch_client_info = await bot.fetchUserInfo(bot.uid)
        client_info = fetch_client_info[bot.uid]
        print("Logged in as", bot.name)

    try:
        await bot.listen()
    except Exception as e:
        print(e)


asyncio.run(main()) 

```


## 🔧 Requirements

- Python 3.9+
- aiohttp
- aiomqtt
- aenum


### 📄 License

This project is distributed under a dual-license model:

- **BSD-3-Clause License**: Parts of the code are reused and adapted from the original [fbchat](https://github.com/fbchat-dev/fbchat) library, licensed under the BSD-3-Clause License. 
  See [LICENSE-BSD](./LICENSE-BSD.md) for details.

- **GPL v3 License**: New contributions and modifications by Muhammad MuQiT/togashigreat are licensed under the GPL v3.0 License.
See [LICENSE](./LICENSE.md) for details.

