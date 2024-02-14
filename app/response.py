import asyncio
from typing import Any

import httpx


BASE_URL = "http://localhost:8080/"


async def hello_world(cli: httpx.AsyncClient) -> tuple[int, dict[str, str]]:
    resp = await cli.get(f"{BASE_URL}hello_world/")
    return resp.status_code, resp.json()


async def create_user(
    cli: httpx.AsyncClient, user_data: dict[str, str]
) -> tuple[int, dict[str, str]]:
    resp = await cli.post(f"{BASE_URL}users/", json=user_data)
    return resp.status_code, resp.json()


async def get_user(
    cli: httpx.AsyncClient, user_id: int
) -> tuple[int, dict[str, str]]:
    resp = await cli.get(f"{BASE_URL}users/{user_id}")
    return resp.status_code, resp.json()


async def update_user(
    cli: httpx.AsyncClient, user_id: int, data_json: dict[str, Any]
) -> tuple[int, dict[str, str]]:
    resp = await cli.patch(f"{BASE_URL}users/{user_id}", json=data_json)
    return resp.status_code, resp.json()


async def delete_user(cli: httpx.AsyncClient, user_id: int):
    resp = await cli.delete(f"{BASE_URL}users/{user_id}")
    return resp.status_code, resp.json()


async def main() -> None:
    async with httpx.AsyncClient() as cli:
        print(await hello_world(cli))
        print(
            await create_user(
                cli,
                {"name": "motherfucker", "password": "123"},
            )
        )
        print(
            await update_user(
                cli, 1, {"name": "Motherfucker", "password": "fuck"}
            )
        )
        print(await get_user(cli, 1))

        print(await delete_user(cli, 1))


if __name__ == "__main__":
    asyncio.run(main())
