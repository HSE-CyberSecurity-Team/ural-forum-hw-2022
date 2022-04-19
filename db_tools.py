import motor.motor_asyncio
import asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)

async def do_insert():
    db = client['ural_data']
    result = await db['vk'].insert_many([{"timestamp": 1649721600, "response_time": 100}, {"timestamp": 1649722600, "response_time": 80},
    {"timestamp": 1649723600, "response_time": 110}, {"timestamp": 1649724600, "response_time": 150},
    {"timestamp": 1649725600, "response_time": 200}, {"timestamp": 1649761600, "response_time": 120}])
    # print('inserted %d docs' % (len(result.inserted_ids),))
# async def add_service():
#     db = client['ural_data']
#     result = await db['apps'].insert_many(
#         [{"name": "vk", "url": "https://vk.com", "active": True},
#          {"name": "google", "url": "https://google.com", "active": True}])

async def do_insert2():
    db = client['ural_data']
    result = await db['emails'].insert_one({"email": "example@example.com", "services": ["vk", "google"]})

# loop = asyncio.get_event_loop()
# loop.run_until_complete(do_insert2())
print('awd')