from typing import Optional, List
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
from email.message import EmailMessage
import aiosmtplib
import aiohttp


class Service(BaseModel):
    name: str
    url: str
    active: bool

class EmailForm(BaseModel):
    email: str
    services: List[str]


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

def avgResponseTime(appStructure : List):
    sum = 0
    for i in appStructure:
        sum += i['response_time']
    return sum / len(appStructure)

async def sendEmail(email : str, app, time):
    message = EmailMessage()
    message["From"] = "ServicesMonitoring@HorizonCorp.org"
    message["To"] = email
    message["Subject"] = "Problems with app {app_name}".format(app_name=app['name'])
    message.set_content("There are some problems with service {app_name} at {app_url}. Average response time is {time}".format(app_name=app['name'],
                                                                                               app_url=app['url'], time=time))
    await aiosmtplib.send(message, hostname="127.0.0.1", port=1025)

async def response_time(url):
    async with aiohttp.ClientSession() as session:

        pokemon_url = url
        t1 = time.time()
        async with session.get(pokemon_url) as resp:
            pokemon = await resp.read()
            t2 = time.time()
            result_time = (t2 - t1) * 1000
            # print('response time:', (t2-t1) * 1000)
            return result_time


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

@app.post("/email")
async def add_email(email: EmailForm):
    # return email.__dict__
    db = client['ural_data']
    collection = db['emails']
    r = await collection.find_one({"email": email.email}, {'_id': 0})
    if r is None:
        collection.insert_one({"email": email.email, "services": email.services})
        return "added new email"
    else:
        collection.update_one({"email": email.email}, {"$set": {"services": email.services}})
        return "mailing preferences updated"


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
@repeat_every(seconds=5)  # 1 hour
async def get_statuses() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]

        if doc["active"]:
            responseTime = await response_time(doc['url'])
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": responseTime})
    return


# TODO
# @app.on_event("startup")

# @repeat_every(seconds=60*60*24)  # 1 day
@app.get('/send-mail')
async def get_statuses() -> None:
    db = client['ural_data']
    collection_emails = db['emails']
    collection_apps = db['apps']
    apps = []
    emailsToSend = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        apps.append(doc)
    async for doc in collection_emails.find({}, {'_id': 0}):
        emailsToSend.append(doc)

    # return apps, emailsToSend
    for app in apps:
        app_collection = db[app['name']]
        responseTimes = []
        async for doc in app_collection.find({'timestamp': {'$gt': day_ago(2)}}, {'_id': 0}):
            responseTimes.append(doc)

        avgTime = avgResponseTime(responseTimes)
        if avgTime > 100:
            for email in emailsToSend:
                if app['name'] in email['services']:
                    await sendEmail(email['email'], app, avgTime)

        return
    # return
    # async for doc in collection_apps.find({}, {'_id': 0}):
    #     if problemWith(app):
    #         async for email in collection_emails.find({"services": ***})
    #             message = EmailMessage()
    #             message["From"] = "root@localhost"
    #             message["To"] = "somebody@example.com"
    #             message["Subject"] = "Hello World!"
    #             message.set_content("Sent via aiosmtplib")
    # return



@app.get("/do_crone")  # 1 hour
async def get_statuses() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]
        if doc["active"]:
            responseTime = await response_time(doc['url'])
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": responseTime})
    return