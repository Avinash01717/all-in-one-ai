from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, User, Tool, UserLog, init_db
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import os

# Create DB tables
init_db()

app = FastAPI()

# Add Session Middleware (Replace 'secret-key' with a strong random string in production)
app.add_middleware(SessionMiddleware, secret_key="super-secret-key-please-change")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Password Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    new_password: str

# --- Auth Helpers ---

# --- Auth Helpers ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user_id(request: Request):
    return request.session.get("user_id")

import re

def validate_password_strength(password: str):
    if len(password) < 9:
        raise HTTPException(status_code=400, detail="Password must be at least 9 characters long")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one symbol")
    return True


# --- Views ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if get_current_user_id(request):
        return RedirectResponse(url="/home")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if not get_current_user_id(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/subcategories", response_class=HTMLResponse)
async def subcategories(request: Request, type: str):
    if not get_current_user_id(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("subcategories.html", {"request": request, "type": type})

@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request, type: str, category: str):
    if not get_current_user_id(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("tools.html", {"request": request, "type": type, "category": category})

# --- API Endpoints ---

@app.post("/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    validate_password_strength(user.password)

    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Create valid session
    request.session["user_id"] = user.id
    
    # Log Login Activity
    new_log = UserLog(user_id=user.id, login_time=datetime.now())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    # Store log id in session so we can update it on logout
    request.session["activity_id"] = new_log.id
    
    return {"message": "Login successful"}

@app.post("/auth/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    # Log Logout Activity
    activity_id = request.session.get("activity_id")
    if activity_id:
        log_entry = db.query(UserLog).filter(UserLog.id == activity_id).first()
        if log_entry:
            log_entry.logout_time = datetime.now()
            db.commit()

    request.session.clear()
    return {"message": "Logged out"}

@app.post("/auth/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Email verified. Please reset your password."}

@app.post("/auth/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    validate_password_strength(data.new_password)

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@app.get("/api/categories")
async def get_categories(type: str, db: Session = Depends(get_db)):
    results = db.query(Tool.category).filter(Tool.type == type).distinct().all()
    categories = [r[0] for r in results]
    return categories

@app.get("/api/tools")
async def get_tools(type: str = None, category: str = None, db: Session = Depends(get_db)):
    query = db.query(Tool)
    if type:
        query = query.filter(Tool.type == type)
    if category:
        query = query.filter(Tool.category == category)
    
    return query.all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
