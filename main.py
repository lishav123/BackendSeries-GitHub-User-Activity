import asyncio
from httpx import AsyncClient
from rich import print

async def fetchGh(name):
    async with AsyncClient() as client:
        response = await client.get(f"https://api.github.com/users/{name}/events")
        return response.json()

async def main():
    resp = await fetchGh("lishav123")
    print(resp)
    print(resp[0].keys())
    print(len(resp))
    print(resp[0])

if __name__ == '__main__':
    asyncio.run(main())