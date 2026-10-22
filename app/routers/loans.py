from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_connection

router = APIRouter(prefix="/loans", tags=["Loans"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_loans(request: Request):
    with get_connection() as conn:
        loans = conn.execute(
            """
            SELECT
                l.id,
                l.borrowed_at,
                l.due_date,
                l.returned_at,
                l.status,
                b.title AS book_title,
                r.full_name AS reader_name
            FROM loans AS l
            JOIN books AS b ON b.id = l.book_id
            JOIN readers AS r ON r.id = l.reader_id
            ORDER BY l.id DESC
            """
        ).fetchall()

        books = conn.execute(
            """
            SELECT id, title, available_quantity
            FROM books
            ORDER BY title
            """
        ).fetchall()

        readers = conn.execute(
            """
            SELECT id, full_name
            FROM readers
            ORDER BY full_name
            """
        ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="loans.html",
        context={
            "title": "Quản lý mượn trả",
            "loans": loans,
            "books": books,
            "readers": readers,
            "today": date.today().isoformat(),
        },
    )


@router.post("/create")
def create_loan(
    book_id: int = Form(...),
    reader_id: int = Form(...),
    due_date: str = Form(...),
):
    try:
        parsed_due_date = date.fromisoformat(due_date)
    except ValueError:
        return HTMLResponse(
            "Ngày hẹn trả không hợp lệ.",
            status_code=400,
        )

    if parsed_due_date < date.today():
        return HTMLResponse(
            "Ngày hẹn trả không được nằm trong quá khứ.",
            status_code=400,
        )

    with get_connection() as conn:
        book = conn.execute(
            """
            SELECT id, available_quantity
            FROM books
            WHERE id = %s
            FOR UPDATE
            """,
            (book_id,),
        ).fetchone()

        if not book:
            return HTMLResponse(
                "Không tìm thấy sách.",
                status_code=404,
            )

        if book["available_quantity"] < 1:
            return HTMLResponse(
                "Sách hiện không còn bản nào có thể cho mượn.",
                status_code=409,
            )

        reader = conn.execute(
            "SELECT id FROM readers WHERE id = %s",
            (reader_id,),
        ).fetchone()

        if not reader:
            return HTMLResponse(
                "Không tìm thấy độc giả.",
                status_code=404,
            )

        conn.execute(
            """
            INSERT INTO loans (book_id, reader_id, due_date)
            VALUES (%s, %s, %s)
            """,
            (book_id, reader_id, parsed_due_date),
        )

        conn.execute(
            """
            UPDATE books
            SET available_quantity = available_quantity - 1
            WHERE id = %s
            """,
            (book_id,),
        )

    return RedirectResponse(
        url="/loans/",
        status_code=303,
    )


@router.post("/{loan_id}/return")
def return_loan(loan_id: int):
    with get_connection() as conn:
        loan = conn.execute(
            """
            SELECT id, book_id, status
            FROM loans
            WHERE id = %s
            FOR UPDATE
            """,
            (loan_id,),
        ).fetchone()

        if not loan:
            return HTMLResponse(
                "Không tìm thấy phiếu mượn.",
                status_code=404,
            )

        if loan["status"] != "borrowed":
            return HTMLResponse(
                "Phiếu mượn này đã được trả trước đó.",
                status_code=409,
            )

        conn.execute(
            """
            UPDATE loans
            SET status = 'returned',
                returned_at = CURRENT_DATE
            WHERE id = %s
            """,
            (loan_id,),
        )

        conn.execute(
            """
            UPDATE books
            SET available_quantity = available_quantity + 1
            WHERE id = %s
            """,
            (loan["book_id"],),
        )

    return RedirectResponse(
        url="/loans/",
        status_code=303,
    )
