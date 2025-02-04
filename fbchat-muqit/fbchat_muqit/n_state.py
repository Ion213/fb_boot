from __future__ import annotations

import aiohttp
import re
import random

from yarl import URL
from typing import Dict

from dataclasses import dataclass, field
from .n_util import * 

from . import _graphql 
from .models import _exception

__all__ = ["State"]

def get_session(cookies: Dict | None = None)-> aiohttp.ClientSession:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.facebook.com/",
        "Host": "www.facebook.com",
        "Origin": "https://www.facebook.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip", #, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    } 

    session = aiohttp.ClientSession(headers=headers, cookies=cookies)

    return session


def get_user_id(session: aiohttp.ClientSession)-> str:
        cookies = session.cookie_jar.filter_cookies(URL("https://www.facebook.com"))
        CookiesDict = {name: cookie.value for name, cookie in cookies.items()}
        return str(CookiesDict.get("c_user"))


def client_id_factory()-> str:
      return hex(int(random.random() * 2 ** 31))[2:]

def save_html(html):
    with open("./test.html", "w") as f:
        f.write(html)

@dataclass
class State:

    user_id: str = field()
    _host: str = field()
    _fb_dtsg: str = field()
    _revision: int | None = field()
    _client_id: str = field(default_factory=client_id_factory)
    _session: aiohttp.client.ClientSession = field(default_factory=get_session)
    _counter: int = field(default=0)
    HEADERS : dict = field(default_factory=dict)

    def get_params(self):
        self._counter += 1

        return {
            "__a": 1,   
            "__req": decimal_to_base36(self._counter),
            "__rev": self._revision,
            "fb_dtsg": self._fb_dtsg
        }

    def adjust_header(self, url):
        host = str(URL(url).host)
        url = f"https://{host}"
        self.HEADERS["Host"] = host
        self.HEADERS["Origin"] = url
        self.HEADERS["Referer"] = f"{url}/"
        return url


    @classmethod
    async def from_cookies(cls, cookies)-> State:
        session = get_session(cookies=cookies)
        return await cls.from_session(session)


    @classmethod
    async def from_json_cookies(cls, json_cookies_path: str)-> State:
        """pass the saved facebook cookies json file to

        Args:
            json_cookies_path (str): the saved facebook cookies json file.

        Returns:
            State: returns an instance of State class with session.
        """
        cookies = get_cookie(json_cookies_path)
        session = get_session(cookies=cookies)
        return await cls.from_session(session)

    @classmethod
    async def from_session(cls, session: aiohttp.client.ClientSession):
        user_id = get_user_id(session)
        url = "https://www.facebook.com/"
        host = "www.facebook.com"

        async with session.get(url, allow_redirects=False) as response:
            if 300 <= response.status < 400:
                """Due to the Changes in network sometimes need to change host"""
                location = response.headers.get('Location')
                host = str(URL(str(location)).host)
                url = f"https://{host}/"
                session.headers["Host"] = host
                session.headers["Origin"] = f"https://{host}"
                session.headers["Referer"] = url
                response = await session.get(url)
            results = await response.text()

        fb_dtsg = re.search(r'"DTSGInitialData".*?"token":"(.*?)"', results)
        if fb_dtsg:
            fb_dtsg = fb_dtsg.group(1)
        else:
            raise ValueError("fb_dtsg not found.")
        clientRevision = re.search(r'client_revision":(\d+)', results)
        if clientRevision:
            clientRevision = int(clientRevision.group(1))

        return cls(
            user_id = user_id,
            _host = host,
            _fb_dtsg = fb_dtsg,
            _revision = clientRevision,
            _session = session,
            HEADERS = dict(session.headers)
        )

    async def is_logged_in(self)-> bool:
        """Sends request to facebook to check login status"""
        try:
            req = await self._session.get(f"https://{self._host}/profile.php", allow_redirects=False)
        except aiohttp.ClientError as e:
            raise Exception("Client Error: ", e)
        location = req.headers.get("Location")
        return str(location) == f"https://{self._host}/profile.php?id={self.user_id}"



    def get_cookies(self):
        cookies = self._session.cookie_jar.filter_cookies(URL("https://www.facebook.com"))
        return {name: cookie.value for name, cookie in cookies.items()}


    
    async def _do_refresh(self):
        # TODO: Raise the error instead, and make the user do the refresh manually
    # It may be a bad idea to do this in an exception handler, if you have a better method
        new = await State.from_session(session=self._session)
        self.user_id = new.user_id
        self._fb_dtsg = new._fb_dtsg
        self._revision = new._revision
        self._counter = new._counter
        self._logout_h = new._logout_h

    async def _get(self, url: str, params: Dict, error_retries=3):
        params.update(self.get_params())
        response = await self._session.get(prefix_url(url, self._host), params=params)
        content = await check_request(response)
        json_data = to_json(content)
        try:
            handle_payload_error(json_data)
        except:
            if error_retries > 0:
                await self._do_refresh()
                return await self._get(url, params, error_retries=error_retries)
            raise
        return json_data


    async def _post(self, url: str, data, files=None, as_graphql=False, error_retries=3)-> dict:
        data.update(self.get_params())
        headers = self.HEADERS
        self._session.headers.clear()
        if files:
            formData = aiohttp.FormData()
            for key, value in data.items():
                formData.add_field(key, str(value))
            for key, (name, file, content_type) in files.items():
                formData.add_field(key, file, filename=name, content_type=content_type)

            data = formData 
            # Let aiohttp automatically handle Content-Type
            headers.pop("Content-Type", None)

        response = await self._session.post(prefix_url(url, self._host), data=data, headers=headers)

        content = await check_request(response)
        self._session._default_headers = self._session._prepare_headers(self.HEADERS)
        try:
            if as_graphql:
                return _graphql.response_to_json(content)
            else:
                j = to_json(content)
                handle_payload_error(j)
                return j
        except aiohttp.ClientResponseError as e:
            if error_retries > 0:
                await self._do_refresh()
                return await self._post(url, data=data, files=files, as_graphql=as_graphql, error_retries=(error_retries - 1))
            raise e

    async def _payload_post(self, url, data, files=None):
        response: Dict = await self._post(url, data=data, files=files)
        try:
            return response["payload"]
            
        except (KeyError, TypeError):
            raise aiohttp.ClientPayloadError(f"missing payload: {response}")
            
    async def _graphql_requests(self, *queries):
        data = {
            "method": "GET",
            "response_format": "json",
            "queries": _graphql.queries_to_json(*queries),
        }
        return await self._post("/api/graphqlbatch/", data, as_graphql=True)

    async def _upload(self, files, voice_clip=False):

        file_dict = {f"upload_{i}": file for i, file in enumerate(files)}
        data = {"voice_clip": voice_clip}
        json_response: dict = await self._payload_post("https://upload.facebook.com/ajax/mercury/upload.php", data, files=file_dict)
        if len(json_response["metadata"]) != len(files):
            return f"Some files could not be uploaded: {json_response}, {files}"
        to_return = [
            (data[1][mimetype_to_key(data[1]["filetype"])], data[1]["filetype"]) 
            for data in json_response["metadata"].items()
        ]
        return to_return

    async def do_send_request(self, data):
        offline_threading_id = generateOfflineThreadingID()
        data["client"] = "mercury"
        data["author"] = f"fbid:{self.user_id}"
        data["timestamp"] = now_time()
        data["source"] = "source:chat:web"
        data["offline_threading_id"] = offline_threading_id
        data["message_id"] = offline_threading_id
        data["threading_id"] = generateMessageID(self._client_id)
        data["ephemeral_ttl_mode:"] = "0"
        json_response = await self._post("/messaging/send/", data)        
        # update JS token if received in response
        fb_dtsg = get_jsmods_require(json_response, 2)
        if fb_dtsg is not None:
            self._fb_dtsg = fb_dtsg

        try:
            message_ids = [
                (action["message_id"], action["thread_fbid"])
                for action in json_response["payload"]["actions"]
                if "message_id" in action
            ]
            if len(message_ids) != 1:
                print("Got multiple message ids' back: {}".format(message_ids))
            return message_ids[0]
        except (KeyError, IndexError, TypeError):
            raise _exception.FBchatException(
                "Error when sending message: "
                f"No message IDs could be found: {json_response}"
            )

