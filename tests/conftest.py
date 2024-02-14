import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db_server import Base
from app.server import UserView, hello_world


engine = create_async_engine("sqlite+aiosqlite://", echo=True)
Sessions = async_sessionmaker(engine, expire_on_commit=False)


async def orm_context(
    app: web.Application,
):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Sessions() as session:
        request["session"] = session
        return await handler(request)


@pytest.fixture
def cli(event_loop: asyncio.AbstractEventLoop, aiohttp_client) -> TestClient:
    app = web.Application()
    app.router.add_post("/users/", UserView)
    app.router.add_get(r"/users/{user_id:\d+}", UserView)
    app.router.add_delete(r"/users/{user_id:\d+}", UserView)
    app.router.add_patch(r"/users/{user_id:\d+}", UserView)
    app.router.add_get("/hello_world/", hello_world)
    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_middleware)

    return event_loop.run_until_complete(aiohttp_client(app))
