from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI
from typing import AsyncIterator
from server.mcp import search
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(search.mcp.session_manager.run())
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/search", search.mcp.streamable_http_app())
