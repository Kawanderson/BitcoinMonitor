import asyncio
import aiohttp

class PriceMonitor:
    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coinbase.com/v2/prices/spot?currency=USD") as resp:
                if resp.ok:
                    return await resp.json()
    

loop = asyncio.get_event_loop()
loop.run_until_complete(PriceMonitor().fetch())