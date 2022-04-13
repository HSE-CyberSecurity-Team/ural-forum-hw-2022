import motor.motor_asyncio
import asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)

async def do_insert():
    db = client['ural_data']
    result = await db['vk'].insert_many([{"timestamp": 1649099304, "response_time": 100}, {"timestamp": 1649099204, "response_time": 80},
    {"timestamp": 1649099104, "response_time": 110}, {"timestamp": 1649099004, "response_time": 150},
    {"timestamp": 1649098904, "response_time": 200}, {"timestamp": 1649098804, "response_time": 120}])
    # print('inserted %d docs' % (len(result.inserted_ids),))
async def add_service():
    db = client['ural_data']
    result = await db['apps'].insert_many(
        [{"name": "vk", "url": "https://vk.com", "active": True},
         {"name": "google", "url": "https://google.com", "active": True}])
# loop = asyncio.get_event_loop()
# loop.run_until_complete(add_service())