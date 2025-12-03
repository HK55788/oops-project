# domain/services.py
from datetime import date
from typing import List, Optional

from .entities import Book, Member, Loan, RegularMember, PremiumMember
from ..repositories.sqlite_repository import Repository


class LibraryService:
    """High‑level business logic."""

    def __init__(self, repo: Repository):
        self.repo = repo

    # ----- Books -----
    def add_book(self, book: Book):
        self.repo.save_book(book)

    def find_book_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.repo.get_book(isbn)

    def list_books(self) -> List[Book]:
        return self.repo.list_books()

    # ----- Members -----
    def add_member(self, member: Member):
        self.repo.save_member(member)

    def find_member_by_id(self, mid: int) -> Optional[Member]:
        return self.repo.get_member(mid)

    def list_members(self) -> List[Member]:
        return self.repo.list_members()

    # ----- Loans -----
    def create_loan(self, isbn: str, member_id: int) -> Loan:
        book = self.find_book_by_isbn(isbn)
        member = self.find_member_by_id(member_id)

        if not book or not member:
            raise ValueError("Book or Member does not exist")

        # enforce borrow limit
        current_loans = [
            l for l in self.repo.list_loans() if l.member_id == member_id
        ]
        if len(current_loans) >= member.borrow_limit():
            raise RuntimeError("Borrow limit reached")

        loan = Loan(
            loan_id=self.repo.next_loan_id(),
            book_isbn=isbn,
            member_id=member_id,
            loan_date=date.today()
        )
        self.repo.save_loan(loan)
        return loan

    def return_book(self, loan_id: int) -> float:
        """Return a book and calculate late fee."""
        loan = self.repo.get_loan(loan_id)
        if not loan:
            raise ValueError("Loan not found")

        member = self.find_member_by_id(loan.member_id)
        today = date.today()
        days_late = loan.days_overdue(today)

        fee = 0.0
        if isinstance(member, PremiumMember):
            fee = member.late_fee(days_late)
        elif days_late > 0:
            fee = days_late * 1.0  # normal rate

        self.repo.delete_loan(loan_id)
        return fee
