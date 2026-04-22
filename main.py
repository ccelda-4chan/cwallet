import asyncio
import subprocess
import json
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from holehe import core as holehe_core
from holehe import modules as holehe_modules
import httpx

import os
from motor.motor_asyncio import AsyncIOMotorClient
import shodan
from censys.search import CensysHosts

# Environment variables for API keys
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
CENSYS_API_ID = os.getenv("CENSYS_API_ID")
CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Database setup
client = AsyncIOMotorClient(MONGO_URI)
db = client.osint_db
collection = db.scans
settings_collection = db.settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simple in-memory storage for tasks and settings
tasks = {}
SETTINGS = {
    "shodan": bool(SHODAN_API_KEY),
    "censys": bool(CENSYS_API_ID and CENSYS_API_SECRET),
    "holehe": True,
    "sherlock": True
}

async def load_settings():
    global SETTINGS
    try:
        # Attempt to load from MongoDB with a 5s timeout
        saved_settings = await asyncio.wait_for(
            settings_collection.find_one({"_id": "global_settings"}), 
            timeout=5.0
        )
        if saved_settings:
            SETTINGS.update(saved_settings.get("config", {}))
        else:
            # Save defaults if not present
            await settings_collection.update_one(
                {"_id": "global_settings"},
                {"$set": {"config": SETTINGS}},
                upsert=True
            )
    except Exception as e:
        print(f"Warning: MongoDB settings load failed: {e}")

@app.on_event("startup")
async def startup_event():
    await load_settings()

async def save_scan(task_id: str, data: dict):
    try:
        await collection.insert_one({
            "task_id": task_id,
            "type": data["type"],
            "target": data["target"],
            "status": data["status"],
            "results": data.get("results"),
            "error": data.get("error"),
            "timestamp": asyncio.get_event_loop().time()
        })
    except Exception as e:
        print(f"Warning: MongoDB save failed: {e}")

async def run_shodan(ip: str, task_id: str):
    tasks[task_id]["status"] = "processing"
    try:
        if not SHODAN_API_KEY:
            raise Exception("Shodan API key missing")
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.host(ip)
        tasks[task_id]["results"] = results
    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"
    finally:
        tasks[task_id]["status"] = "completed"
        await save_scan(task_id, tasks[task_id])

async def run_holehe(email: str, task_id: str):
    tasks[task_id]["status"] = "processing"
    out = []
    # In holehe 1.61, import_submodules returns a dict {name: module_object}
    modules_dict = holehe_core.import_submodules("holehe.modules")
    
    async with httpx.AsyncClient() as client:
        for module in modules_dict.values():
            try:
                # 1.61 uses (email, client, out)
                await module.check(email, client, out)
            except Exception:
                pass
                
    tasks[task_id]["results"] = out
    tasks[task_id]["status"] = "completed"
    await save_scan(task_id, tasks[task_id])

async def run_sherlock(username: str, task_id: str):
    tasks[task_id]["status"] = "processing"
    try:
        # Run sherlock as a subprocess
        # Sherlock project on PyPI uses 'sherlock' command or 'python -m sherlock_project'
        process = subprocess.run(
            ["python", "-m", "sherlock_project", username, "--json"],
            capture_output=True,
            text=True
        )
        
        # Sherlock usually creates {username}.json when --json is used
        filename = f"{username}.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
            tasks[task_id]["results"] = data
            os.remove(filename) # Clean up
        else:
            # Try to see if it's in the output
            try:
                data = json.loads(process.stdout)
                tasks[task_id]["results"] = data
            except:
                tasks[task_id]["error"] = "Sherlock produced no JSON output"
                tasks[task_id]["status"] = "failed"
                return

    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"
    finally:
        tasks[task_id]["status"] = "completed"
        await save_scan(task_id, tasks[task_id])

@app.post("/scan/ip")
async def scan_ip(background_tasks: BackgroundTasks, ip: str = Form(...)):
    if not SETTINGS.get("shodan"):
        return JSONResponse({"error": "Shodan is disabled in settings"}, status_code=400)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"type": "shodan", "target": ip, "status": "pending", "results": None}
    background_tasks.add_task(run_shodan, ip, task_id)
    return JSONResponse({"task_id": task_id})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "settings": SETTINGS})

@app.get("/settings")
async def get_settings():
    return SETTINGS

@app.post("/settings")
async def update_settings(new_settings: dict):
    global SETTINGS
    SETTINGS.update(new_settings)
    try:
        await settings_collection.update_one(
            {"_id": "global_settings"},
            {"$set": {"config": SETTINGS}},
            upsert=True
        )
    except Exception as e:
        print(f"Warning: MongoDB settings update failed: {e}")
    return SETTINGS

@app.post("/scan/email")
async def scan_email(background_tasks: BackgroundTasks, email: str = Form(...)):
    if not SETTINGS.get("holehe"):
        return JSONResponse({"error": "Holehe is disabled in settings"}, status_code=400)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"type": "holehe", "target": email, "status": "pending", "results": None}
    background_tasks.add_task(run_holehe, email, task_id)
    return JSONResponse({"task_id": task_id})

@app.post("/scan/username")
async def scan_username(background_tasks: BackgroundTasks, username: str = Form(...)):
    if not SETTINGS.get("sherlock"):
        return JSONResponse({"error": "Sherlock is disabled in settings"}, status_code=400)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"type": "sherlock", "target": username, "status": "pending", "results": None}
    background_tasks.add_task(run_sherlock, username, task_id)
    return JSONResponse({"task_id": task_id})

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(tasks[task_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
