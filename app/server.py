import json
from datetime import datetime

from aiohttp import web
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_server import Base, User, async_session, engine


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = web.Application()


def get_hash_password(password: str) -> str:
    hash_pass = pwd_context.hash(password)
    return hash_pass


def validate_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


async def orm_context(app: web.Application):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with async_session() as session:
        request["session"] = session
        return await handler(request)


async def get_user(user_id: int, session: AsyncSession):
    user = await session.get(User, user_id)
    if not user:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "User not found"}),
            content_type="application/json",
        )
    return user


class UserView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request["session"]

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    async def get(self):
        user = await get_user(self.user_id, self.session)
        return web.json_response(
            {
                "id": user.id,
                "name": user.name,
                "password": user.password,
                "creted_at": datetime.timestamp(user.created_at),
            }
        )

    async def post(self):
        json_data = await self.request.json()
        json_data["password"] = get_hash_password(json_data["password"])
        user = User(**json_data)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as err:
            raise web.HTTPConflict(
                text=json.dumps({"error": "User already exists"}),
                content_type="application/json",
            ) from err
        return web.json_response({"id": user.id})

    async def patch(self):
        user = await get_user(self.user_id, self.session)
        json_data = await self.request.json()
        if "password" in json_data:
            json_data["password"] = get_hash_password(json_data["password"])
        for field, value in json_data.items():
            setattr(user, field, value)
        await self.session.commit()
        return web.json_response({"status": "success"})

    async def delete(self):
        user = await get_user(self.user_id, self.session)
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"status": "success"})


async def hello_world(request: web.Request):
    return web.json_response({"text": "hello motherfucker"})


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)
app.add_routes(
    [
        web.get("/hello_world/", hello_world),
        web.post("/users/", UserView),
        web.get(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/users/{user_id:\d+}", UserView),
    ]
)
if __name__ == "__main__":
    web.run_app(app)
