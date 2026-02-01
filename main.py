from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize Firebase (Admin SDK)
# Note: You will need to provide your service account key path here or via environment variable
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/subcategories", response_class=HTMLResponse)
async def subcategories(request: Request, type: str):
    # type will be 'paid' or 'unpaid'
    return templates.TemplateResponse("subcategories.html", {"request": request, "type": type})

@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request, type: str, category: str):
    return templates.TemplateResponse("tools.html", {"request": request, "type": type, "category": category})

@app.get("/api/categories")
async def get_categories(type: str):
    import json
    with open("tools_data.json", "r", encoding="utf-8") as f:
        tools = json.load(f)
    
    # Filter by type and extract unique categories
    categories = set()
    for tool in tools:
        if tool.get("type") == type:
            categories.add(tool.get("category"))
    return list(categories)

@app.get("/api/tools")
async def get_tools(type: str = None, category: str = None):
    import json
    try:
        with open("tools_data.json", "r", encoding="utf-8") as f:
            tools = json.load(f)
        
        filtered = tools
        if type:
            filtered = [t for t in filtered if t.get("type") == type]
        if category:
            filtered = [t for t in filtered if t.get("category") == category]
            
        return filtered
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
