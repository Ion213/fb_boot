import random
import time
import json
import sys
import asyncio
from typing import List, Set, Tuple
import aiohttp
from os.path import basename 
from mimetypes import guess_type
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs
from yarl import URL


def save_cookies_to_session(session: aiohttp.ClientSession, cookies):
    """
    Save cookies from a list to an aiohttp.ClientSession.
    
    Args:
        session (aiohttp.ClientSession): The client session to update.
        cookies (list): A list of cookies in the format:
            [{'key': 'name', 'value': 'value'}, ...]
    """
        # Add modified cookie for Messenger domain
    messenger_domain = 'www.messenger.com'
    session.cookie_jar.update_cookies(
        cookies,
        response_url=URL(f"https://{messenger_domain}")
            )


def now_time()-> int:
    "returns current time"
    return int(time.time() * 1000)


def configure_event_loop():
    """Configure the asyncio event loop based on the Windows OS."""
    if sys.platform.lower().startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def to_json(content)-> dict:
    """Removes `for(;;);` (and other cruft) that preceeds JSON responses."""
    try:
        content = content[content.index("{"):]
        return json.loads(content)
    except Exception as e:
        raise ValueError("Failed parsing Json", e)


def digitToChar(digit):
    if digit < 10:
        return str(digit)
    return chr(ord("a") + digit - 10)


def str_base(number, base):
    if number < 0:
        return "-" + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digitToChar(m)
    return digitToChar(m)



def decimal_to_base36(decimal_num)->str:
    if not isinstance(decimal_num, int):
        raise ValueError("Input must be an integer.")
    if decimal_num == 0:
        return "0"
    base36_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []
    while decimal_num:
        decimal_num, remainder = divmod(decimal_num, 36)
        result.append(base36_chars[remainder])

    return ''.join(result[::-1])



def check_http_code(status_code: int):
    msg = f"Error when sending request: Got {status_code} response"
    if status_code == 404:
        print(f"{msg}\nThis is either because you specified an invalid URL, or because you provided an invalid id (Facebook usually requires integer ids")
    elif 400 <=status_code < 600:
        print(msg)


async def check_request(response)-> str:
    check_http_code(response.status)
    content = await response.text()
    if content is None or not len(content):
        raise ValueError("Error When sending request: Got empty response")
    return content



def prefix_url(url: str, host = None)-> URL:

    """Adds https://www.facebook.com or https://web.facebook.com"""

    if str(url).startswith("/") and host:
        return URL(f"https://{host}{url}")

    elif str(url).startswith("/"):
        return URL(f"https://www.facebook.com{url}")

    return URL(url)



def generateMessageID(client_id=None)-> str:
      k = now_time()
      lame = int(random.random() * 4294967295)
      return f"<{k}:{lame}-{client_id}@mail.projektitan.com>"


def getSignatureID()->str:
    return hex(int(random.random() * 2147483648))


def generateOfflineThreadingID()-> str:
    ret = now_time()
    value = int(random.random() * 4294967295)
    string = ("0000000000000000000000" + format(value, "b"))[-22:]
    msgs = format(ret, "b") + string
    return str(int(msgs, 2))

def require_list(list_)-> Set[str]:
      if isinstance(list_, list):
         return set(list_)
      else:
         return set([list_])

def handle_payload_error(j):
    if "error" not in j:
        return
    error_code = j["error"]
    if error_code == 1357001:
        print("FBChat not logged in")
    elif error_code == 1357004:
        print("Error: please refresh your cookies!")
    elif error_code in (1357031, 1545010, 1545003):
        print("Error: Invalid Parameters")
    else:
        print("FBchatError")

def handle_graphql_error(response):
    """Handles Erros"""
    errors = []
    if response.get("error"):
        errors = [response["error"]]
    elif "errors" in response:
        errors = response["error"]
    if errors:
        error = errors[0]
        print(f"Error:  error-code: {error.get('code')} error-message: {error.get('message')}")
 

def mimetype_to_key(mimetype) -> str:
    """This function is used when sending files, images"""
    if not mimetype:
        return "file_id"  # Default for unknown mimetypes
    
    mimetype = mimetype.strip()  # Remove leading/trailing whitespace
    if mimetype == "image/gif":
        return "gif_id"
    
    parts = mimetype.split("/")
    if len(parts) == 2 and parts[0] in ["video", "image", "audio"]:
        return f"{parts[0]}_id"
    
    return "file_id"  # Default for unsupported types


def get_jsmods_require(j, index):
    if j.get("jsmods") and j["jsmods"].get("require"):
        try:
            return j["jsmods"]["require"][0][index][0]
        except (KeyError, IndexError):
            print(
                "Error when getting jsmods_require: {}. Facebook might have changed protocol".format(j)
            )
    return None


async def get_files_from_urls(file_urls)-> List[Tuple[str, bytes, str]]:
    files = []
    async with aiohttp.ClientSession() as session:
        for file_url in file_urls:
            async with session.get(file_url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"Failed to fetch {file_url}",
                    )
                file_name = basename(file_url).split("?")[0].split("#")[0]
                content_type = response.headers.get("Content-Type") or guess_type(file_name)[0]
                content = await response.read()  # Read the content as bytes
                files.append(
                    (
                        file_name,
                        content,  # Use bytes, not StreamReader
                        content_type,
                    )
                )
    return files


@contextmanager
def get_files_from_paths(filenames):
    files = []
    for filename in filenames:
        files.append(
            (basename(filename), open(filename, "rb"), guess_type(filename)[0])
        )
    yield files
    for fn, fp, ft in files:
        fp.close()


def get_url_parameters(url, *args):
    params = parse_qs(urlparse(url).query)
    return [params[arg][0] for arg in args if params.get(arg)]


def get_url_parameter(url, param):
    return get_url_parameters(url, param)[0]


def get_cookie(json_path: str) -> dict:
    """Get ans Format cookies before passing to session"""
    with open(json_path, "r") as f:
        data = json.load(f)
    cookies = {}
    for cookie in data:
        cookies[cookie["key"]] = cookie["value"]
    return cookies
