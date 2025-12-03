# domain/entities.py
from abc import ABC, abstractmethod
import re
from datetime import date, timedelta


class Entity(ABC):
    """Base class for all domain objects."""
    @abstractmethod
    def to_dict(self) -> dict:
        """Return a serialisable representation."""
        pass


# ---------- Books ----------
class Book(Entity):
    ISBN_RE = re.compile(r"^\d{10}(\d{3})?$")

    def __init__(self, isbn: str, title: str, author: str, price: float):
        if not self.ISBN_RE.match(isbn):
            raise ValueError(f"Invalid ISBN: {isbn}")
        self.__isbn = isbn          # encapsulated
        self.title = title
        self.author = author
        self.price = price

    @property
    def isbn(self) -> str:
        return self.__isbn

    def to_dict(self):
        return {
            "type": "Book",
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "price": self.price,
        }


class PhysicalBook(Book):
    def __init__(self, isbn: str, title: str, author: str,
                 price: float, weight_kg: float, shelf_location: str):
        super().__init__(isbn, title, author, price)
        self.weight_kg = weight_kg
        self.shelf_location = shelf_location

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {"type": "PhysicalBook",
             "weight_kg": self.weight_kg,
             "shelf_location": self.shelf_location}
        )
        return d


class Ebook(Book):
    def __init__(self, isbn: str, title: str, author: str,
                 price: float, file_format: str, download_link: str):
        super().__init__(isbn, title, author, price)
        self.file_format = file_format
        self.download_link = download_link

    def to_dict(self):
        d = super().to_dict()
        d.update(
            {"type": "Ebook",
             "file_format": self.file_format,
             "download_link": self.download_link}
        )
        return d


# ---------- Members ----------
class Member(Entity, ABC):
    def __init__(self, member_id: int, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email

    @abstractmethod
    def borrow_limit(self) -> int:
        pass

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email
        }


class RegularMember(Member):
    def borrow_limit(self) -> int:
        return 5


class PremiumMember(Member):
    def borrow_limit(self) -> int:
        return 10

    # Premium members get an extra day for returns
    def late_fee(self, days_late: int) -> float:
        return max(0, (days_late - 1)) * 0.50


# ---------- Loans ----------
class Loan(Entity):
    def __init__(self, loan_id: int, book_isbn: str,
                 member_id: int, loan_date: date):
        self.loan_id = loan_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.loan_date = loan_date
        self.due_date = loan_date + timedelta(days=14)

    def is_overdue(self, today: date) -> bool:
        return today > self.due_date

    def days_overdue(self, today: date) -> int:
        if not self.is_overdue(today):
            return 0
        return (today - self.due_date).days

    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "book_isbn": self.book_isbn,
            "member_id": self.member_id,
            "loan_date": self.loan_date.isoformat(),
            "due_date": self.due_date.isoformat()
        }
