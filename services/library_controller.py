# services/library_controller.py
from typing import List

from ..domain.entities import Book, Member, Loan
from ..repositories.sqlite_repository import Repository
from .library_service import LibraryService


class LibraryController:
    """Acts as the mediator between UI and domain."""

    def __init__(self, repo: Repository):
        self.service = LibraryService(repo)

    # ---------- Books ----------
    def add_book(self, book: Book):
        self.service.add_book(book)

    def get_books(self) -> List[Book]:
        return self.service.list_books()

    # ---------- Members ----------
    def add_member(self, member: Member):
        self.service.add_member(member)

    def get_members(self) -> List[Member]:
        return self.service.list_members()

    # ---------- Loans ----------
    def loan_book(self, isbn: str, member_id: int) -> Loan:
        return self.service.create_loan(isbn, member_id)

    def return_book(self, loan_id: int) -> float:
        """Return book and get late fee."""
        return self.service.return_book(loan_id)
