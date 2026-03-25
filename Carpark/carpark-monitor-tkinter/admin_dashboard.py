import tkinter as tk
from tkinter import ttk

from Callum import CallumMixin
from Jack import JackMixin
from Paris import ParisMixin
from Jenna import JennaMixin


class CarParkAdminDashboard(
    CallumMixin,
    JackMixin,
    ParisMixin,
    JennaMixin,
    tk.Tk
):
    # Main app file.

    def __init__(self):
        tk.Tk.__init__(self)

        # window setup
        self.title("CCCU Car Park Monitor - Admin Login")
        self.geometry("420x300")
        self.minsize(420, 300)

        #admin login
        self.admin_username = "admin"
        self.admin_password = "admin"

        # database and dropdown
        self.db = None
        self.car_park_choices = []

        # style
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # main window grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # login variables
        self.login_username_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        self.login_frame = None

        # builds first screen
        self.build_login_screen()


if __name__ == "__main__":
    app = CarParkAdminDashboard()
    app.mainloop()