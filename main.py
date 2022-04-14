from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import motor.motor_asyncio
from fastapi_utils.tasks import repeat_every
import requests as rq
from pydantic import BaseModel
from pathlib import Path


class Service(BaseModel):
    name: str
    url: str
    active: bool


client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)

def day_ago(days_ago):
    now = time.time()
    day_start = int(now - (now % 86400))
    # yday = time.localtime(day_start - 86400 * days_ago)  # seconds/day
    # start = time.struct_time((yday.tm_year, yday.tm_mon, yday.tm_mday, 0, 0, 0, 0, 0, yday.tm_isdst))
    # today = time.localtime(now)
    # end = time.struct_time((today.tm_year, today.tm_mon, today.tm_mday, 0, 0, 0, 0, 0, today.tm_isdst))
    return day_start - 86400 * days_ago

def timestampToDaysAgo(timestamp):
    now = time.time()
    return int(now - timestamp) // 86400


def addToDb(app_id):
    return True

def deleteFromDb(app_id):
    return True

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
templates = Jinja2Templates(directory="static/templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", context={'request': request})


@app.get("/app_lists")
async def app_lists():
    db = client['ural_data']
    collection = db['apps']
    dummy_list = []
    async for doc in collection.find({}, {'_id': 0}):
        dummy_list.append(doc)
    return dummy_list


@app.get("/health/{app_id}")
async def get_item(app_id: str, q: Optional[str] = None):
    dummy_json = {1649099304: 100, 1649099204: 80, 1649099104: 110, 1649099004: 150, 1649098904: 200, 1649098804: 120}

    db = client['ural_data']
    collection = db[app_id]
    dummy_list = []
    temp = 0
    amount = 0
    async for doc in collection.find({}, {'_id': 0}):
        dummy_list.append(doc)

    # return dummy_list

    times_dict = dict()
    amount_dict = dict()
    for j in dummy_list:
        temp = 0
        daysAgo = timestampToDaysAgo(j['timestamp'])
        amount = 0
        if daysAgo not in times_dict.keys():
            times_dict[daysAgo] = j['response_time']
            amount_dict[daysAgo] = 1
        else:
            times_dict[daysAgo] += j['response_time']
            amount_dict[daysAgo] += 1
    for i in times_dict:
        times_dict[i] /= amount_dict[i]

    return times_dict

@app.options("/add")
async def add_item_cors_shit(response: Response):
    response
    response.headers["Content-type"] ="application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    # response.__setitem__("Access-Control-Allow-Origin", "*")
    return {"status" : "success"}

@app.options("/app_lists")
async def add_item_cors_shit(response: Response):
    response
    response.headers["Content-type"] ="application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    # response.__setitem__("Access-Control-Allow-Origin", "*")
    return {"status" : "success"}

@app.post("/add")
async def add_item(service: Service):
    db = client['ural_data']
    collection = db['apps']
    # service["active"] = True
    # d = dict(service)
    # return await collection.count_documents({"name": service.name})
    # return service.__dict__
    if await collection.count_documents({"name": service.name}) == 0:
        collection.insert_one(service.__dict__)
        return service.__dict__
    else:
        return "app already exists"

@app.delete("/health/{app_id}")
async def delete_item(app_id: str, q: Optional[str] = None):
    # delete items from db
    db = client['ural_data']
    collection = db['apps']
    collection.update_one({"name": app_id}, {"$set": {"active": False}})
    return True

@app.patch("/health/{app_id}")
def replace_item(old_app_id: str, new_app_id: str):
    # delete items from db
    deleteFromDb(old_app_id)
    addToDb(new_app_id)

    return True


@app.on_event("startup")
@repeat_every(seconds=60*60)  # 1 hour
async def get_statuses() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]
        if doc["active"]:
            response = rq.get(doc['url'])#говнокод - нужен асинхронный requests
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": response.elapsed.total_seconds() * 1000})
    return



@app.get("/do_crone")  # 1 hour
async def get_statuses() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]
        if doc["active"] == "True":
            response = rq.get(doc['url'])
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": response.elapsed.total_seconds() * 1000})
    return