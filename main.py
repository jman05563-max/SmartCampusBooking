
from database import create_tables, insert_campuses, insert_resources
from authentication import ensure_demo_accounts
from gui import SmartCampusApp
import tkinter as tk


def main():
    create_tables()
    insert_campuses()
    insert_resources()
    ensure_demo_accounts()

    root = tk.Tk()
    app = SmartCampusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
