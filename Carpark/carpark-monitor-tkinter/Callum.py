import tkinter as tk
from tkinter import ttk, messagebox

from shared_db import DB_PATH, DatabaseManager


class CallumMixin:
    # Callum - work on this file
    # Login screen, dashboard startup, header and notebook tabs.

    def build_login_screen(self):
        self.login_frame = ttk.Frame(self, padding=24)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.columnconfigure(0, weight=1)

        card = ttk.LabelFrame(self.login_frame, text="Admin login", padding=18)
        card.grid(row=0, column=0, sticky="n", pady=(16, 0))
        card.columnconfigure(1, weight=1)

        ttk.Label(
            card,
            text="CCCU Car Park Monitor",
            font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(
            card,
            text="Please sign in before accessing the admin dashboard.",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        ttk.Label(card, text="Username").grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        username_entry = ttk.Entry(
            card,
            textvariable=self.login_username_var,
            width=28
        )
        username_entry.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(card, text="Password").grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        password_entry = ttk.Entry(
            card,
            textvariable=self.login_password_var,
            show="*",
            width=28
        )
        password_entry.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Button(
            card,
            text="Login",
            command=self.try_login
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        self.bind("<Return>", self.try_login)
        username_entry.focus_set()

    def try_login(self, event=None):
        username = self.login_username_var.get().strip()
        password = self.login_password_var.get()

        if username == self.admin_username and password == self.admin_password:
            self.unbind("<Return>")

            if self.login_frame is not None:
                self.login_frame.destroy()

            self.show_dashboard()
        else:
            messagebox.showerror(
                "Login failed",
                "Incorrect username or password."
            )
            self.login_password_var.set("")

    def show_dashboard(self):
        self.title("CCCU Car Park Monitor - Admin Dashboard")
        self.geometry("1680x980")
        self.minsize(1320, 820)
        self.rowconfigure(1, weight=1)

        self.db = DatabaseManager(DB_PATH)
        self.car_park_choices = self.db.car_park_options()

        self.build_header()
        self.build_notebook()
        self.refresh_all()
        self.start_auto_refresh()

    def build_header(self):
        header = ttk.Frame(self, padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="CCCU Car Park Monitor",
            font=("Segoe UI", 20, "bold")
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text=(
                "Admin dashboard for reviewing permit applications, issuing permits, "
                "managing visitors, reservations, patrol checks and penalty notices."
            ),
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.permits_tab = ttk.Frame(self.notebook, padding=12)
        self.issued_permits_tab = ttk.Frame(self.notebook, padding=12)
        self.visitors_tab = ttk.Frame(self.notebook, padding=12)
        self.reservations_tab = ttk.Frame(self.notebook, padding=12)
        self.temp_permits_tab = ttk.Frame(self.notebook, padding=12)
        self.checker_tab = ttk.Frame(self.notebook, padding=12)
        self.penalties_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.permits_tab, text="Permit Applications")
        self.notebook.add(self.issued_permits_tab, text="Issued Permits")
        self.notebook.add(self.visitors_tab, text="Visitor Bookings")
        self.notebook.add(self.reservations_tab, text="Reservations")
        self.notebook.add(self.temp_permits_tab, text="Temporary / Day Permits")
        self.notebook.add(self.checker_tab, text="Permit Check")
        self.notebook.add(self.penalties_tab, text="Penalty Notices")

        self.build_dashboard_tab()
        self.build_permits_tab()
        self.build_issued_permits_tab()
        self.build_visitors_tab()
        self.build_reservations_tab()
        self.build_temp_permits_tab()
        self.build_checker_tab()
        self.build_penalties_tab()