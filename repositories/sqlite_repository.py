# repositories/sqlite_repository.py
import sqlite3
from datetime import date
from typing import List, Optional

from ..domain.entities import Book, Member, Loan


class Repository:
    """Concrete SQLite implementation of CRUD operations."""

    def __init__(self, db_path: str = "db/library.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    # ---------- Helper ----------
    def _execute(self, sql: str, params=(), commit=False):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        if commit:
            self.conn.commit()
        return cur

    # ---------- Tables ----------
    def _create_tables(self):
        self._execute("""
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                type TEXT,
                title TEXT, author TEXT, price REAL,
                weight_kg REAL, shelf_location TEXT,
                file_format TEXT, download_link TEXT
            )
        """, commit=True)

        self._execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY,
                type TEXT,
                name TEXT, email TEXT
            )
        """, commit=True)

        self._execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY,
                book_isbn TEXT, member_id INTEGER,
                loan_date TEXT, due_date TEXT
            )
        """, commit=True)

    # ---------- Books ----------
    def save_book(self, book: Book):
        d = book.to_dict()
        self._execute("""
            INSERT OR REPLACE INTO books
            (isbn, type, title, author, price,
             weight_kg, shelf_location,
             file_format, download_link)
            VALUES (:isbn, :type, :title, :author, :price,
                    :weight_kg, :shelf_location,
                    :file_format, :download_link)
        """, d, commit=True)

    def get_book(self, isbn: str) -> Optional[Book]:
        cur = self._execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        row = cur.fetchone()
        if not row:
            return None
        # Reconstruct the correct subclass
        type_ = row[1]
        if type_ == "PhysicalBook":
            return PhysicalBook(*row[2:])  # use from entities
        if type_ == "Ebook":
            return Ebook(*row[2:])
        return Book(row[1], row[2], row[3], row[4])

    def list_books(self) -> List[Book]:
        cur = self._execute("SELECT * FROM books")
        rows = cur.fetchall()
        return [self.get_book(r[0]) for r in rows]

    # ---------- Members ----------
    def save_member(self, member: Member):
        d = member.to_dict()
        self._execute("""
            INSERT OR REPLACE INTO members
            (member_id, type, name, email)
            VALUES (:member_id, :type, :name, :email)
        """, d, commit=True)

    def get_member(self, member_id: int) -> Optional[Member]:
        cur = self._execute("SELECT * FROM members WHERE member_id=?", (member_id,))
        row = cur.fetchone()
        if not row:
            return None
        type_ = row[1]
        if type_ == "RegularMember":
            return RegularMember(row[0], row[2], row[3])
        if type_ == "PremiumMember":
            return PremiumMember(row[0], row[2], row[3])
        return None

    def list_members(self) -> List[Member]:
        cur = self._execute("SELECT * FROM members")
        rows = cur.fetchall()
        return [self.get_member(r[0]) for r in rows]

    # ---------- Loans ----------
    def save_loan(self, loan: Loan):
        d = loan.to_dict()
        self._execute("""
            INSERT OR REPLACE INTO loans
            (loan_id, book_isbn, member_id,
             loan_date, due_date)
            VALUES (:loan_id, :book_isbn, :member_id,
                    :loan_date, :due_date)
        """, d, commit=True)

    def get_loan(self, loan_id: int) -> Optional[Loan]:
        cur = self._execute("SELECT * FROM loans WHERE loan_id=?", (loan_id,))
        row = cur.fetchone()
        if not row:
            return None
        loan_date = date.fromisoformat(row[3])
        due_date = date.fromisoformat(row[4])
        return Loan(row[0], row[1], row[2], loan_date)

    def delete_loan(self, loan_id: int):
        self._execute("DELETE FROM loans WHERE loan_id=?", (loan_id,), commit=True)

    def list_loans(self) -> List[Loan]:
        cur = self._execute("SELECT * FROM loans")
        rows = cur.fetchall()
        return [self.get_loan(r[0]) for r in rows]

    # ---------- Utility ----------
    def next_loan_id(self) -> int:
        cur = self._execute("SELECT MAX(loan_id) FROM loans")
        row = cur.fetchone()
        return (row[0] or 0) + 1
