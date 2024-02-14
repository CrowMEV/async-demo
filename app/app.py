import asyncio
from typing import Any, AsyncIterator, Iterator, Sequence

import aiohttp

from app.db import Base, engine, past_to_db


# from itertools import islice


# def chunk(arr_range, arr_size):
#     arr_range = iter(arr_range)
#     return iter(lambda: tuple(islice(arr_range, arr_size)), ())


# class AsyncIter:

#     async def __aiter__(self):
#         pass

#     async def __anext__(self):
#         pass


API_URL = "https://swapi.dev/api/people/"
MAX_REQUESTS = 5


def chunked(seq: Sequence[Any], chunk_size: int) -> Iterator[Sequence[Any]]:
    for i in range(0, len(seq), chunk_size):
        yield seq[i : i + chunk_size]


async def get_people(client: aiohttp.ClientSession, people_id: int) -> dict:
    async with client.get(f"{API_URL}{people_id}") as response:
        return await response.json()


async def people_generator(
    start: int, end: int
) -> AsyncIterator[dict[str, Any]]:
    async with aiohttp.ClientSession() as client:
        for i in range(start, end):
            async with client.get(f"{API_URL}{i}") as response:
                yield await response.json()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with aiohttp.ClientSession() as client:
        for id_chunk in chunked(range(1, 51), MAX_REQUESTS):
            result = await asyncio.gather(
                *[get_people(client, people_id) for people_id in id_chunk]
            )
            asyncio.create_task(past_to_db(result))
    tasks = asyncio.all_tasks() - {
        asyncio.current_task(),
    }
    for task in tasks:
        await task


if __name__ == "__main__":
    asyncio.run(main())
