import asyncio
from httpx import AsyncClient
from rich import print

def parse(data: dict) -> str:
    if data["type"] == "CreateEvent":
        return f"{data["actor"]["login"]} created the repo {data["repo"]["name"]}"

async def fetchGh(name):
    async with AsyncClient() as client:
        response = await client.get(f"https://api.github.com/users/{name}/events")
        return list(map(parse, response.json()))

async def main():
    resp = await fetchGh("lishav123")
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())