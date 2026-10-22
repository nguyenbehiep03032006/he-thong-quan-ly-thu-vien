from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_connection

router = APIRouter(prefix="/readers", tags=["Readers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_readers(request: Request):
    with get_connection() as conn:
        readers = conn.execute(
            """
            SELECT id, full_name, email, phone, address
            FROM readers
            ORDER BY id DESC
            """
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="readers.html",
        context={"title": "Quản lý độc giả", "readers": readers},
    )


@router.post("/create")
def create_reader(
    full_name: str = Form(...),
    email: str = Form(default=""),
    phone: str = Form(default=""),
    address: str = Form(default=""),
):
    full_name = full_name.strip()
    email = email.strip() or None
    phone = phone.strip() or None
    address = address.strip() or None

    if not full_name:
        return HTMLResponse(
            "Họ tên độc giả không được để trống.",
            status_code=400,
        )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO readers (full_name, email, phone, address)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, phone, address),
        )

    return RedirectResponse(url="/readers/", status_code=303)
