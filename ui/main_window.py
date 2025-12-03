# ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from ..services.library_controller import LibraryController
from ..domain.entities import PhysicalBook, Ebook, RegularMember, PremiumMember


class MainWindow(tk.Tk):
    """Simple Tkinter UI – only the core actions are shown."""

    def __init__(self, controller: LibraryController):
        super().__init__()
        self.title("Library Management System")
        self.controller = controller
        self._build_widgets()

    def _build_widgets(self):
        # Buttons
        ttk.Button(self, text="Add Book", command=self.add_book).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self, text="Add Member", command=self.add_member).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self, text="Loan Book", command=self.loan_book).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self, text="Return Book", command=self.return_book).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self, text="Show Books", command=self.show_books).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(self, text="Show Members", command=self.show_members).grid(row=0, column=5, padx=5, pady=5)

        # Text area
        self.text = tk.Text(self, width=80, height=25)
        self.text.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

    # ---------- Callbacks ----------
    def add_book(self):
        isbn = simpledialog.askstring("ISBN", "Enter ISBN:")
        title = simpledialog.askstring("Title", "Book Title:")
        author = simpledialog.askstring("Author", "Author Name:")
        price = float(simpledialog.askstring("Price", "Price:"))
        book_type = simpledialog.askstring("Type", "Physical or Ebook? (P/E)")

        if book_type.upper() == 'P':
            weight = float(simpledialog.askstring("Weight", "Weight (kg):"))
            shelf = simpledialog.askstring("Shelf", "Shelf location:")
            book = PhysicalBook(isbn, title, author, price, weight, shelf)
        else:
            fmt = simpledialog.askstring("Format", "File format (pdf, epub):")
            link = simpledialog.askstring("Link", "Download link:")
            book = Ebook(isbn, title, author, price, fmt, link)

        self.controller.add_book(book)
        messagebox.showinfo("Success", "Book added.")

    def add_member(self):
        mid = int(simpledialog.askstring("ID", "Member ID:"))
        name = simpledialog.askstring("Name", "Full Name:")
        email = simpledialog.askstring("Email", "Email:")
        mem_type = simpledialog.askstring("Type", "Regular or Premium? (R/P)")

        if mem_type.upper() == 'R':
            member = RegularMember(mid, name, email)
        else:
            member = PremiumMember(mid, name, email)

        self.controller.add_member(member)
        messagebox.showinfo("Success", "Member added.")

    def loan_book(self):
        isbn = simpledialog.askstring("ISBN", "Book ISBN:")
        mid = int(simpledialog.askstring("Member ID", "Member ID:"))
        try:
            loan = self.controller.loan_book(isbn, mid)
            messagebox.showinfo("Success", f"Loan created. ID: {loan.loan_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_book(self):
        loan_id = int(simpledialog.askstring("Loan ID", "Enter Loan ID:"))
        try:
            fee = self.controller.return_book(loan_id)
            messagebox.showinfo("Returned", f"Book returned. Late fee: ${fee:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_books(self):
        books = self.controller.get_books()
        self.text.delete(1.0, tk.END)
        for b in books:
            self.text.insert(tk.END, f"{b.isbn} – {b.title} by {b.author}\n")

    def show_members(self):
        members = self.controller.get_members()
        self.text.delete(1.0, tk.END)
        for m in members:
            self.text.insert(tk.END, f"{m.member_id} – {m.name}\n")
