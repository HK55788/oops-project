# main.py
import os

from repositories.sqlite_repository import Repository
from services.library_controller import LibraryController
from ui.main_window import MainWindow

# Ensure db folder exists
os.makedirs("db", exist_ok=True)

if __name__ == "__main__":
    repo = Repository()
    controller = LibraryController(repo)
    app = MainWindow(controller)
    app.mainloop()
