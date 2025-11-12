import asyncio
import ssl

from websockets.legacy.server import serve

from gdo.base.Message import Message
from gdo.core.Connector import Connector

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.websocket.module_websocket import module_websocket


class Websocket(Connector):

    def module_websocket(self) -> 'module_websocket':
        from gdo.websocket.module_websocket import module_websocket
        return module_websocket.instance()

    async def gdo_connect(self) -> bool:
        self._connected = True
        asyncio.create_task(self.mainloop())
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
        async with serve(self.handler, mod.cfg_ip(), mod.cfg_port(), ssl=ssl_context):
            await asyncio.Future()

    async def handler(self, ws):
        async for msg in ws:
            await ws.send(f"echo: {msg}")

    async def gdo_send_to_user(self, msg: Message, notice: bool=False):
        pass
