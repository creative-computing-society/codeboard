from aiohttp import ClientSession

_session: ClientSession | None = None  # Will be set to ClientSession at startup


# This will set ClientSession for each gunicorn worker
async def get_session() -> ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = ClientSession()

    return _session


async def close_session():
    global _session

    if _session and not _session.closed:
        await _session.close()


def set_session(session: ClientSession):
    global _session
    _session = session
