import pytest
from aiohttp.test_utils import TestClient


@pytest.mark.asyncio
async def test_hello_world(cli: TestClient):
    resp = await cli.get("/hello_world/")
    assert resp.status == 200
    assert await resp.json() == {"text": "hello motherfucker"}


async def test_create_user(cli: TestClient):
    resp = await cli.post(
        "/users/", json={"name": "user_1", "password": "123"}
    )
    assert resp.status == 200
    assert await resp.json() == {"id": 1}


async def test_create_user_duplicate(cli: TestClient):
    await cli.post("/users/", json={"name": "user_1", "password": "123"})
    resp = await cli.post(
        "/users/", json={"name": "user_1", "password": "123"}
    )
    assert resp.status == 409
    assert await resp.json() == {"error": "User already exists"}


async def test_get_user(cli: TestClient):
    await cli.post("/users/", json={"name": "user_1", "password": "123"})
    resp = await cli.get("/users/1")
    user_data = await resp.json()
    assert resp.status == 200
    assert user_data["name"] == "user_1"


async def test_delete_user(cli: TestClient):
    await cli.post("/users/", json={"name": "user_1", "password": "123"})
    resp = await cli.delete("/users/1")
    assert resp.status == 200
    assert await resp.json() == {"status": "success"}
    resp = await cli.get("/users/1")
    assert resp.status == 404
    assert await resp.json() == {"error": "User not found"}


async def test_update_user(cli: TestClient):
    await cli.post("/users/", json={"name": "user_1", "password": "123"})
    original_user = await cli.get("/users/1")
    original_user_data = await original_user.json()
    data = {"name": "Motherfucker", "password": "fuck"}
    await cli.patch("/users/1", json=data)
    user = await cli.get("/users/1")
    user_data = await user.json()
    assert user.status == 200
    assert user_data["name"] != original_user_data["name"]
    assert user_data["password"] != original_user_data["password"]
