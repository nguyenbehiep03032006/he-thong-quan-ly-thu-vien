from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_connection

router = APIRouter(prefix="/books", tags=["Books"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_books(request: Request):
    with get_connection() as conn:
        books = conn.execute(
            """
            SELECT id, isbn, title, author, publisher,
                   published_year, category, quantity,
                   available_quantity
            FROM books
            ORDER BY id DESC
            """
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="books.html",
        context={"title": "Quản lý sách", "books": books},
    )


@router.post("/create")
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(default=""),
    category: str = Form(default=""),
    quantity: int = Form(default=1),
):
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip() or None
    category = category.strip() or None

    if not title or not author or quantity < 0:
        return HTMLResponse(
            "Tên sách, tác giả phải có giá trị và số lượng không được âm.",
            status_code=400,
        )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO books
                (isbn, title, author, category,
                 quantity, available_quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (isbn, title, author, category, quantity, quantity),
        )

    return RedirectResponse(url="/books/", status_code=303)


@router.get("/{book_id}/edit", response_class=HTMLResponse)
def edit_book_page(request: Request, book_id: int):
    with get_connection() as conn:
        book = conn.execute(
            "SELECT * FROM books WHERE id = %s",
            (book_id,),
        ).fetchone()

    if not book:
        return HTMLResponse("Không tìm thấy sách.", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="edit_book.html",
        context={"title": "Sửa thông tin sách", "book": book},
    )


@router.post("/{book_id}/edit")
def update_book(
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(default=""),
    category: str = Form(default=""),
    quantity: int = Form(...),
):
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip() or None
    category = category.strip() or None

    if not title or not author or quantity < 0:
        return HTMLResponse(
            "Tên sách, tác giả phải có giá trị và số lượng không được âm.",
            status_code=400,
        )

    with get_connection() as conn:
        current = conn.execute(
            """
            SELECT quantity, available_quantity
            FROM books
            WHERE id = %s
            FOR UPDATE
            """,
            (book_id,),
        ).fetchone()

        if not current:
            return HTMLResponse("Không tìm thấy sách.", status_code=404)

        borrowed_count = current["quantity"] - current["available_quantity"]

        if quantity < borrowed_count:
            return HTMLResponse(
                "Số lượng mới không thể nhỏ hơn số sách đang được mượn.",
                status_code=400,
            )

        conn.execute(
            """
            UPDATE books
            SET title = %s,
                author = %s,
                isbn = %s,
                category = %s,
                quantity = %s,
                available_quantity = %s
            WHERE id = %s
            """,
            (
                title, author, isbn, category,
                quantity, quantity - borrowed_count, book_id,
            ),
        )

    return RedirectResponse(url="/books/", status_code=303)


@router.post("/{book_id}/delete")
def delete_book(book_id: int):
    with get_connection() as conn:
        book = conn.execute(
            "SELECT id FROM books WHERE id = %s",
            (book_id,),
        ).fetchone()

        if not book:
            return HTMLResponse("Không tìm thấy sách.", status_code=404)

        has_loans = conn.execute(
            "SELECT EXISTS(SELECT 1 FROM loans WHERE book_id = %s)",
            (book_id,),
        ).fetchone()["exists"]

        if has_loans:
            return HTMLResponse(
                "Không thể xóa sách đã có lịch sử mượn.",
                status_code=409,
            )

        conn.execute("DELETE FROM books WHERE id = %s", (book_id,))

    return RedirectResponse(url="/books/", status_code=303)
