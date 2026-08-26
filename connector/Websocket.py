import asyncio
import threading
from asyncio import AbstractEventLoop

import msgspec.json
from websocket_server import WebsocketServer, WebSocketHandler

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.core.Connector import Connector

from typing import TYPE_CHECKING

from gdo.core.GDO_Session import GDO_Session
from gdo.core.GDO_User import GDO_User

if TYPE_CHECKING:
    from gdo.websocket.module_websocket import module_websocket


class Websocket(Connector):

    ws: WebsocketServer
    handlers: dict[str,GDO_User]
    inited: bool

    def __init__(self):
        super().__init__()
        self.handlers = {}
        self.inited = False

    def get_render_mode(self) -> Mode:
        return Mode.render_html

    def render_user_connect_help(self) -> str:
        return t('help_ws_connect')

    def module_websocket(self) -> 'module_websocket':
        from gdo.websocket.module_websocket import module_websocket
        return module_websocket.instance()

    async def gdo_connect(self) -> bool:
        self._connected = True
        asyncio.create_task(self.mainloop())
        # asyncio.run(self.mainloop())
        return True

    async def gdo_disconnect(self, quit_message: str) -> bool:
        self._connected = False
        await self.broadcast(quit_message)
        return True

    async def mainloop(self):
        mod = self.module_websocket()
        tls = mod.cfg_tls()
        Logger.debug(f'Listening for websocket connections on {mod.cfg_host()}:{mod.cfg_port()}')
        server = WebsocketServer(host=mod.cfg_host(), port=mod.cfg_port(), cert=mod.cfg_tls_cert_path() if tls else None, key=mod.cfg_tls_key_path() if tls else None)
        server.set_fn_new_client(self.new_client)
        server.set_fn_message_received(self.handler)
        server.set_fn_client_left(self.client_left)
        self._connected = True
        self.ws = server
        server.run_forever(True)
        return True

    def new_client(self, address, ws):
        Logger.debug(f'New client on {address}')
        Logger.debug(f'New client on {ws}')
        wsh: WebSocketHandler = address['handler']
        Application.init_thread(threading.current_thread())

    def get_or_create_connector_user(self, session_user: GDO_User) -> GDO_User:
        """Return the WebSocket identity linked to one authenticated web user.

        A browser session belongs to the Web account, while its live socket is
        a distinct connector.  Keeping that distinction makes reply routing
        deterministic: IBDES can emit ``name{ws}`` and ``say.to`` reaches the
        active socket instead of the Web connector's intentional stub.
        """
        user = self._server.get_user_by_name(session_user.get_name())
        if user:
            return user
        user = GDO_User.blank({
            'user_type': session_user.get_user_type(),
            'user_name': session_user.get_name(),
            'user_displayname': session_user.get_displayname(),
            'user_server': self._server.get_id(),
            'user_link': session_user.get_id(),
        }).insert()
        self._server._users[user.get_name()] = user
        return user

    @staticmethod
    def authenticated_session_user(session: GDO_Session) -> GDO_User | None:
        """Return a valid session-bound guest or member, never an anonymous session."""
        user = session.get_user()
        if not session.is_persisted() or not user.is_persisted() or not user.is_user():
            return None
        return user

    def client_left(self, address, ws):
        Logger.debug(f'Client left: {address}')
        wsh: WebSocketHandler = address['handler']
        Application.init_thread(threading.current_thread())
        if hasattr(wsh, 'gdo_user'):
            user = wsh.gdo_user
            del self.handlers[user]

    def handler(self, address, ws, msg: str):
        wsh: WebSocketHandler = address['handler']
        Application.init_thread(threading.current_thread())
        if not hasattr(wsh, 'gdo_user'):
            session = GDO_Session.for_cookie(msg, False)
            session_user = self.authenticated_session_user(session)
            if session_user is None:
                Logger.message('Rejected WebSocket client without an authenticated session.')
                wsh.send_close(1008, b'Authentication required')
                return
            user = self.get_or_create_connector_user(session_user)
            user._authenticated = session_user._authenticated
            Application.set_current_user(user)
            wsh.gdo_user = user
            user._network_user = wsh
            self.handlers[user] = user
            wsh.send_message(t('msg_welcome_ws', (user.render_name(),)))
        else:
            user = wsh.gdo_user
            Logger.debug(f'WS << {user.render_name()} << {msg}')
            Application.tick()
            Application.init_common()
            Application.set_current_user(user)
            message = Message(msg, Mode.render_html).env_user(user, True).env_server(self._server).env_mode(Mode.render_html)
            Application.MESSAGES.put(message)

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        Logger.debug(f'WS >> {msg._env_user.render_name()} >> {msg._result}')
        msg._env_user._network_user.send_message(msg._result)

    async def broadcast(self, msg: str):
        for user in self.handlers.values():
            user._network_user.send_message(msg)
