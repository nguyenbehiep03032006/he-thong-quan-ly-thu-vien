from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_client import make_asgi_app

from app.routers.books import router as books_router
from app.routers.readers import router as readers_router
from app.routers.loans import router as loans_router

app = FastAPI(title="Library Management System")

# Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())

templates = Jinja2Templates(directory="app/templates")

app.include_router(books_router)
app.include_router(readers_router)
app.include_router(loans_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Hệ thống quản lý thư viện"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
