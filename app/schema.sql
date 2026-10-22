CREATE TABLE IF NOT EXISTS books (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    publisher VARCHAR(150),
    published_year INTEGER,
    category VARCHAR(100),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    available_quantity INTEGER NOT NULL DEFAULT 0
        CHECK (available_quantity >= 0 AND available_quantity <= quantity),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS readers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(30),
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id BIGINT NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    reader_id BIGINT NOT NULL REFERENCES readers(id) ON DELETE RESTRICT,
    borrowed_at DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    returned_at DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'borrowed'
        CHECK (status IN ('borrowed', 'returned')),
    CHECK (due_date >= borrowed_at),
    CHECK (returned_at IS NULL OR returned_at >= borrowed_at),
    CHECK (
        (status = 'borrowed' AND returned_at IS NULL)
        OR (status = 'returned' AND returned_at IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_reader_id ON loans(reader_id);
CREATE INDEX IF NOT EXISTS idx_loans_status_due_date
    ON loans(status, due_date);
