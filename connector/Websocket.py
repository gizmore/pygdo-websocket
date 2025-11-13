import asyncio
import ssl

from websockets.server import serve

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector

from typing import TYPE_CHECKING

from gdo.core.GDO_Session import GDO_Session

if TYPE_CHECKING:
    from gdo.websocket.module_websocket import module_websocket


async def handler(ws):
    try:
        async for msg in ws:
            if msg[0].isdigit():
                session = GDO_Session.for_cookie(msg)
                user = session.get_user()
                Application.set_current_user(user)
                user._network_user = ws
                ws._gdo_user = user
                await ws.send("AUTHENTICATED!")
            message = Message(msg, Mode.HTML).env_user(ws._gdo_user).env_server(self._server).env_session(ws._gdo_user._session).env_mode(Mode.HTML)
            Application.MESSAGES.put(message)
    except Exception as e:
        Logger.exception(e)

class Websocket(Connector):

    def module_websocket(self) -> 'module_websocket':
        from gdo.websocket.module_websocket import module_websocket
        return module_websocket.instance()

    async def gdo_connect(self) -> bool:
        self._connected = True
        asyncio.create_task(self.mainloop(), name='websocket')
        return True

    async def gdo_disconnect(self) -> bool:
        pass

    async def mainloop(self):
        mod = self.module_websocket()
        ssl_context = None
        if mod.cfg_tls():
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=mod.cfg_tls_cert_path(),
                                        keyfile=mod.cfg_tls_key_path())
        async with serve(handler, mod.cfg_ip(), mod.cfg_port(), ssl=ssl_context):
            await asyncio.Future()

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        await msg._env_user._network_user.send(msg._message)
