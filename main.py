from typing import Optional, List
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
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
import re
from datetime import datetime


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


def avgResponseTime(appStructure: List):
    sum = 0
    for i in appStructure:
        sum += int(i['response_time'])
    if len(appStructure) != 0:
        return sum / len(appStructure)
    else:
        return 0


async def sendEmail(email: str, app, time, was500=False):
    if was500:
        text = "Service was down at some time with 5xx responses"
    else:
        text = "Service was always up"
    message = EmailMessage()
    # message["From"] = "ServicesMonitoring@HorizonCorp.org"
    message['From'] = "servicesmonitoringhorizoncorp@gmail.com"
    message["To"] = email
    message["Subject"] = "Problems with app {app_name}".format(app_name=app['name'])
    message.set_content(
        "There are some problems with service {app_name} at {app_url}. Average response time is {time} ms. {text}".format(
            app_name=app['name'],
            app_url=app['url'], time=time, text=text))
    # await aiosmtplib.send(message, hostname="127.0.0.1", port=1025)
    try:
        await aiosmtplib.send(message, hostname="smtp.gmail.com", port=587, start_tls=True,
                              username="servicesmonitoringhorizoncorp@gmail.com",
                              password="***")

    except aiosmtplib.errors.SMTPAuthenticationError as e:
        return e


async def response_time_code(url):
    async with aiohttp.ClientSession() as session:
        pokemon_url = url
        t1 = time.time()
        try:
            async with session.get(pokemon_url) as resp:
                pokemon = await resp.read()
                t2 = time.time()
                result_time = (t2 - t1) * 1000
                # print('response time:', (t2-t1) * 1000)
                return result_time, resp.status
        except aiohttp.client_exceptions.ClientConnectorError:
            return 5000, 500


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


@app.get("/{period}_health/{app_id}")
async def get_item(app_id: str, period: str, q: Optional[str] = None):
    if period == "week":
        db = client['ural_data']
        collection = db[app_id]
        dummy_list = []
        temp = 0
        amount = 0

        async for doc in collection.find({'timestamp': {'$gt': day_ago(11)}}, {'_id': 0}):
            dummy_list.append(doc)
        # return dummy_list

        times_dict = dict()
        amount_dict = dict()
        anyError = False
        upTime = 0
        for j in dummy_list:
            temp = 0
            multiplier = 1
            try:
                if int(j['status']) < 500:
                    upTime += 1
                else:
                    multiplier = 100
            except:
                upTime += 1
                pass

            daysAgo = timestampToDaysAgo(j['timestamp'])
            amount = 0
            if daysAgo not in times_dict.keys():
                times_dict[daysAgo] = j['response_time'] * multiplier
                amount_dict[daysAgo] = 1
            else:
                times_dict[daysAgo] += j['response_time'] * multiplier
                amount_dict[daysAgo] += 1
        for i in times_dict:
            times_dict[i] /= amount_dict[i]

        return times_dict, upTime / len(dummy_list)
    elif period == "day":
        db = client['ural_data']
        collection = db[app_id]
        dummy_list = []
        temp = 0
        amount = 0

        async for doc in collection.find({'timestamp': {'$gt': day_ago(1)}}, {'_id': 0}):
            dummy_list.append(doc)
        # return dummy_list

        times_dict = dict()
        anyError = False
        upTime = 0
        for j in dummy_list:
            temp = 0
            multiplier = 1
            try:
                if int(j['status']) < 500:
                    upTime += 1
                else:
                    multiplier = 100
            except:
                upTime += 1
                pass

            # daysAgo = timestampToDaysAgo(j['timestamp'])
            amount = 0
            # if daysAgo not in times_dict.keys():
            times_dict[datetime.utcfromtimestamp(j["timestamp"]).strftime('%H:%M')] = j['response_time'] * multiplier
            # amount_dict[daysAgo] = 1
            # else:
            #     times_dict[daysAgo] += j['response_time'] * multiplier
            #     amount_dict[daysAgo] += 1
        for i in times_dict:
            times_dict[i] /= len(dummy_list)

        return times_dict, upTime / len(dummy_list)


@app.get("/latest/{app_id}")
async def latest_resp(app_id: str):
    db = client['ural_data']
    collection = db[app_id]
    # async for a in collection.find({'_id': 0}).sort("_id", -1).limit(1):
    #     latest = a
    latest = []
    async for a in collection.find({}, {'_id': 0}).sort("_id", -1).limit(1):
        latest.append(a)
    return latest[0]


@app.post("/add")
async def add_item(service: Service, response: Response):
    if not re.match("^[a-zA-Z0-9_-]*$", service.name):
        response.status_code = 422
        return "not suitable name, use only letters and numbers"
    elif not re.match(
            "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
            service.url):
        response.status_code = 422
        return "not suitable url"

    db = client['ural_data']
    collection = db['apps']
    collection_app = db[service.name]

    if service.active:
        res = await response_time_code(service.url)
        collection_app.insert_one({"timestamp": int(time.time()), "response_time": res[0], "status": res[1]})
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
async def add_email(email: EmailForm, response: Response):
    if not re.match("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email.email):
        response.status_code = 422
        return "not correct email format"
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
@repeat_every(seconds=60 * 60)  # 1 hour
async def get_statuses() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]

        if doc["active"]:
            res = await response_time_code(doc['url'])
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": res[0], "status": res[1]})
    return


# @app.on_event("startup")
# @repeat_every(seconds=60 * 60 * 24)  # 1 day
@app.get('/send-mail')
async def send_emails() -> None:
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
        check = False
        code = 200
        app_collection = db[app['name']]
        responseTimes = []
        async for doc in app_collection.find({'timestamp': {'$gt': day_ago(2)}}, {'_id': 0}):
            responseTimes.append(doc)
            if 'status' in doc.keys() and int(doc['status']) >= 500:
                check = True
                code = doc['status']

        avgTime = avgResponseTime(responseTimes)
        if avgTime > 50:
            for email in emailsToSend:
                if app['name'] in email['services']:
                    await sendEmail(email['email'], app, avgTime, was500=check)
        elif check:
            for email in emailsToSend:
                if app['name'] in email['services']:
                    await sendEmail(email['email'], app, avgTime, was500=check)

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
async def get_statuses2() -> None:
    db = client['ural_data']
    collection_apps = db['apps']
    dummy_list = []
    async for doc in collection_apps.find({}, {'_id': 0}):
        collection_app = db[doc['name']]
        if doc["active"]:
            res = await response_time_code(doc['url'])
            collection_app.insert_one({"timestamp": int(time.time()), "response_time": res[0], "status": res[1]})
    return
