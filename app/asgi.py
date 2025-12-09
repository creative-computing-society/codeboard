"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from typing import Callable, Awaitable, Dict, Mapping, Any

from aiohttp import ClientSession
from django.core.asgi import get_asgi_application
from leaderboard import close_session, set_session

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

_application = get_asgi_application()

Recieve = Callable[
    [], Awaitable[Dict]
]  # typehint that indicates a function that takes in no values and returns an couroutine

Send = Callable[
    [Mapping[str, Any]], Awaitable[None]
]  # typehint that indicates a function taking a dictionary with key as str and value as anything and retuning a couroutine


# Since we want every worker to have its own ClientSession, we define it in lifespan
async def application(scope: Dict, receive: Recieve, send: Send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                set_session(ClientSession())
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await close_session()
                await send({"type": "lifespan.shutdown.complete"})
                return
    else:
        await _application(scope, receive, send)
