import socket, json
import asyncio
from websockets.asyncio.server import serve
__ircat_type__ = "none"
__ircat_requires__ = ["ws_config", "webirc_pass"]
class IRCatModule:
    def __init__(self, ws_config, webirc_pass):
        self.password = webirc_pass
        self.cfg = json.loads(open(ws_config).read())
    async def WSprocess(sock):
        writer = asyncio.create_task(self.WSwriter(sock))
        async for message in websocket:
            await websocket.send(message)
        await writer
    async def WSserver(self):
        async with serve(self.WSprocess, "127.0.0.1", 6677) as server:
            await server.serve_forever()
    def onThread(self):
        asyncio.run(self.WSserver())