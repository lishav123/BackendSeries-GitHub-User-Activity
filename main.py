import asyncio
from httpx import AsyncClient
from rich import print

async def main():
    async with AsyncClient() as client:
        response = await client.get("https://dummy-json.mock.beeceptor.com/posts")
        print(f"[bold magenta]{response.json()}[/bold magenta]")

if __name__ == '__main__':
    asyncio.run(main())