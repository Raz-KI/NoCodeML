# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import aioml, salPredLR
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key")

app.include_router(aioml.router)
app.include_router(salPredLR.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(  request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "Hello from FastAPI without JS!"
    })
@app.get("/logout")
def logout(request: Request):
    request.session.clear()  # 🧽 Clears all session data
    return RedirectResponse(url="/", status_code=303)