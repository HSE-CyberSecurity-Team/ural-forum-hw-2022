import aiohttp
import asyncio
import time

async def response_time(url):
    async with aiohttp.ClientSession() as session:

        pokemon_url = url
        t1 = time.time()
        async with session.get(pokemon_url) as resp:
            pokemon = await resp.read()
            t2 = time.time()
            result_time = (t2 - t1) * 1000
            print('response time:', (t2-t1) * 1000)
            return result_time

asyncio.run(response_time("https://hse.ru"))