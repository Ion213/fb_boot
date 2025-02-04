from __future__ import annotations

import aiomqtt
import paho.mqtt.client as mqtt
import random
import aiohttp

from dataclasses import dataclass, field
from typing import Any
from yarl import URL

from . import _graphql, _util
from aiomqtt.exceptions import MqttConnectError
from .n_state import State


@dataclass(slots=True)
class Mqtt:
    _state: State = field()
    _mqttClient: aiomqtt.Client = field()
    _chat_on: bool = field()
    _foreground: bool = field()
    _sequence_id: int = field()
    _sync_token: Any = field(default=None)
    _HOST = "edge-chat.facebook.com"


    @classmethod
    async def connect(cls, state: State, chat_on: bool, foreground: bool)-> Mqtt:

        mqttClint = aiomqtt.Client(
            hostname=cls._HOST,
            identifier="mqttwsclient",
            clean_session=True,
            protocol=aiomqtt.ProtocolVersion.V31,
            transport="websockets",
            port=443,
            keepalive=60
        )
        sequence_id = await cls._fetch_sequence_id(state)
        # needed for websockets
        mqttClint._client.tls_set()
        # creating class instance 
        self = cls(
            _state=state,
            _mqttClient=mqttClint,
            _chat_on=chat_on,
            _foreground=foreground,
            _sequence_id=sequence_id
        )
    
        
        self._configure_connect_options()
        await mqttClint.__aenter__()
        if self._mqttClient._client.is_connected():
            await self._messenger_queue_publish()
        return self

    @staticmethod
    async def _fetch_sequence_id(state)-> int:
        """Fetch sequence ID."""
        params = {
            "limit": 1,
            "tags": ["INBOX"],
            "before": None,
            "includeDeliveryReceipts": False,
            "includeSeqID": True,
            }
        (j,) = await state._graphql_requests(_graphql.from_doc_id("1349387578499440", params))
        sequence_id = j["viewer"]["message_threads"]["sync_sequence_id"] #type: ignore
        return int(sequence_id)



    def _configure_connect_options(self)-> None:
        session_id = generate_session_id()
        topics = [
            "/t_ms",
            "/thread_typing",
            "/orca_typing_notifications",
            "/orca_presence",
            "/legacy_web", "/br_sr", "/sr_res",
            "/ls_req",
            "/ls_resp",
            "/webrtc",
            "/onevc",
            "/notify_disconnect",
            "/mercury",
            "/messaging_events",
            "/orca_message_notifications",
            "/pp",
            "/webrtc_response",
        ]
        username = {
            "u": self._state.user_id,
            "s": session_id,
            "chat_on": self._chat_on,
            "fg": self._foreground,
            "d": self._state._client_id,
            "aid": 219994525426954,
            "st": topics,
            "pm": [],
            "cp": 3,
            "ecp": 10,
            "ct": "websocket",
            "mqtt_sid": "",
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
        }
        self._mqttClient._client.username_pw_set(_util.json_minimal(username))

        headers = {
            "Cookie": get_cookie_header(
                self._state._session, "https://edge-chat.facebook.com/chat"
            ),
            "User-Agent": self._state._session.headers["User-Agent"],
            "Origin": "https://www.facebook.com",
            "Host": self._HOST
        }
        self._mqttClient._client.ws_set_options(
            path=f"/chat?sid={session_id}", headers=headers
        )
        
    
    async def _messenger_queue_publish(self)-> None:
        # configure receiving messages.
        payload = {
            "sync_api_version": 10,
            "max_deltas_able_to_process": 1000,
            "delta_batch_size": 500,
            "encoding": "JSON",
            "entity_fbid": self._state.user_id,
        }

        if self._sync_token is None:
            topic = "/messenger_sync_create_queue"
            payload["initial_titan_sequence_id"] = str(self._sequence_id)
            payload["device_params"] = None
        else:
            topic = "/messenger_sync_get_diffs"
            payload["last_seq_id"] = str(self._sequence_id)
            payload["sync_token"] = self._sync_token

        await self._mqttClient.publish(topic, _util.json_minimal(payload), qos=1)

    # def _on_connect_client(self, client, userdata, flags, reason_code) -> None:
    #     """Called when we receive a CONNACK message from the broker."""
    #     if self._mqttClient._connected.done():
    #         pass
    #     if reason_code == mqtt.CONNACK_ACCEPTED:
    #         self._mqttClient._connected.set_result(None)
    #     else:
    #         # We received a negative CONNACK response
    #         self._mqttClient._connected.set_exception(MqttConnectError(reason_code))


    async def disconnect(self):
        await self._mqttClient.__aexit__(None, None, None)

    async def set_foreground(self, value):
        payload = _util.json_minimal({"foreground": value})
        await self._mqttClient.publish("/foreground_state", payload=payload, qos=1)
        self._foreground = value

    async def set_chat_on(self, value):
        data = {"make_user_available_when_in_foreground": value}
        payload = _util.json_minimal(data)
        await self._mqttClient.publish("/set_client_settings", payload=payload, qos=1)
        self._chat_on = value

def generate_session_id()-> int:
    return random.randint(1, 2 ** 53)


def get_cookie_header(session: aiohttp.ClientSession, url: str) -> str:
    return session.cookie_jar.filter_cookies(URL(url)).output(header="", sep=";").lstrip()

