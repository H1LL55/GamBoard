import tkinter as tk
from tkinter import ttk

from Callum import CallumMixin
from Kris import KrisMixin
from Paris import ParisMixin
#from Jenna import JennaMixin
from Jack import JackMixin


class CarParkAdminDashboard(
    CallumMixin,
    KrisMixin,
    ParisMixin,
    #JennaMixin,
    JackMixin,
    tk.Tk
):
    # Main app file.
    # Run this file to start the admin dashboard.

    def __init__(self):
        tk.Tk.__init__(self)

        # Window setup
        self.title("CCCU Car Park Monitor - Admin Login")
        self.geometry("420x300")
        self.minsize(420, 300)

        # Hard-coded admin login for now
        self.admin_username = "admin"
        self.admin_password = "admin"

        # Database and dropdown data
        self.db = None
        self.car_park_choices = []

        # Style
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Main window grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Login variables
        self.login_username_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        self.login_frame = None

        # Build first screen
        self.build_login_screen()


if __name__ == "__main__":
    app = CarParkAdminDashboard()
    app.mainloop()