import tkinter as tk
from tkinter import ttk, messagebox

from shared_db import (
    DB_PATH,
    COLLECTION_LOCATIONS,
    ISSUED_PERMIT_STATUSES,
    PERMIT_APP_STATUSES,
    PERMIT_KIND_OPTIONS,
    TEMP_PERMIT_OPTIONS,
    DatabaseManager,
    as_yes_no,
    default_collection_for_campus,
    default_expiry_str,
    ensure_date,
    normalise_reg,
    parse_car_park_id,
    parse_date,
    today_str,
)


class CarParkAdminDashboard(tk.Tk):
    # This is the staff side of the system.
    # Applicants should not use this one, they should use permit_application_form.py instead.
    def __init__(self):
        super().__init__()
        self.title("CCCU Car Park Monitor - Admin Login")
        self.geometry("420x260")
        self.minsize(420, 260)

        # Hard-coded login for now just so the admin dashboard is not open to everyone.
        # You asked for admin / admin, so that is what this uses.
        self.admin_username = "admin"
        self.admin_password = "admin"

        self.db = None
        self.car_park_choices = []

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.login_username_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        self.login_frame = None

        self.build_login_screen()

    # ------------------------------
    # Login screen
    # ------------------------------
    def build_login_screen(self):
        self.login_frame = ttk.Frame(self, padding=24)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.columnconfigure(0, weight=1)

        card = ttk.LabelFrame(self.login_frame, text="Admin login", padding=18)
        card.grid(row=0, column=0, sticky="n", pady=(16, 0))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="CCCU Car Park Monitor", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Label(
            card,
            text="Please sign in before accessing the admin dashboard.",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        ttk.Label(card, text="Username").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        username_entry = ttk.Entry(card, textvariable=self.login_username_var, width=28)
        username_entry.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(card, text="Password").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        password_entry = ttk.Entry(card, textvariable=self.login_password_var, show="*", width=28)
        password_entry.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Button(card, text="Login", command=self.try_login).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        # Let Enter submit the login so it feels a bit cleaner.
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
            messagebox.showerror("Login failed", "Incorrect username or password.")
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

    # ------------------------------
    # General window layout
    # ------------------------------
    def build_header(self):
        header = ttk.Frame(self, padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="CCCU Car Park Monitor", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Admin dashboard for reviewing permit applications, issuing permits, managing visitors, reservations, patrol checks and penalty notices.",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

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

    # ------------------------------
    # Dashboard tab
    # ------------------------------
    def build_dashboard_tab(self):
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)

        self.kpi_frame = ttk.Frame(self.dashboard_tab)
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for idx in range(5):
            self.kpi_frame.columnconfigure(idx, weight=1)

        self.kpi_labels = {}
        kpi_titles = [
            ("car_parks", "Car parks"),
            ("total_spaces", "Canterbury total spaces"),
            ("pending_permits", "Pending permit reviews"),
            ("approved_permits", "Approved applications"),
            ("issued_permits", "Issued permits"),
            ("friday_only", "Friday-only permits"),
            ("today_visitors", "Today's visitors"),
            ("active_reservations", "Active reservations"),
            ("active_temporary_permits", "Active temp/day permits"),
            ("penalties", "Penalty notices"),
        ]

        for idx, (key, title) in enumerate(kpi_titles):
            card = ttk.LabelFrame(self.kpi_frame, text=title, padding=12)
            card.grid(row=idx // 5, column=idx % 5, sticky="nsew", padx=6, pady=6)
            label = ttk.Label(card, text="0", font=("Segoe UI", 18, "bold"))
            label.pack(anchor="center", pady=8)
            self.kpi_labels[key] = label

        lower = ttk.Panedwindow(self.dashboard_tab, orient=tk.HORIZONTAL)
        lower.grid(row=1, column=0, sticky="nsew")

        carparks_frame = ttk.LabelFrame(lower, text="Car park overview", padding=8)
        notes_frame = ttk.LabelFrame(lower, text=" ", padding=10)
        lower.add(carparks_frame, weight=3)
        lower.add(notes_frame, weight=2)

        carparks_frame.columnconfigure(0, weight=1)
        carparks_frame.rowconfigure(0, weight=1)

        columns = ("Campus", "Name", "Standard", "Visitor", "Electric", "Disabled", "Total")
        self.carparks_tree = ttk.Treeview(carparks_frame, columns=columns, show="headings", height=16)
        for col in columns:
            self.carparks_tree.heading(col, text=col)
            self.carparks_tree.column(col, width=120, anchor="center")
        self.carparks_tree.column("Name", width=270, anchor="w")
        self.carparks_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(carparks_frame, orient="vertical", command=self.carparks_tree.yview)
        self.carparks_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        notes_text = (
            "• Applicants now submit new permit requests through the separate application form file.\n\n"
            "• This dashboard is staff/admin side only.\n\n"
            "• Permit applications saved in the other file appear here because both files use the same SQLite database.\n\n"
            "• The dashboard auto-refreshes so review staff can see new applications coming in without reopening the whole system.\n\n"
            "• Visitors, reservations, temporary permits, patrol checks and penalty notices need to be accepted here."
        )
        ttk.Label(notes_frame, text=notes_text, justify="left", wraplength=430).pack(fill="both", expand=True)

    # ------------------------------
    # Permit review tab
    # ------------------------------
    def build_permits_tab(self):
        self.permits_tab.columnconfigure(0, weight=1)
        self.permits_tab.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(self.permits_tab, text="Applications and review", padding=8)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        permit_columns = ("ID", "Type", "Campus", "Name", "Reg 1", "Reg 2", "Employment", "Email", "Car park", "Status", "Created")
        self.permits_tree = ttk.Treeview(table_frame, columns=permit_columns, show="headings", height=20)
        for col in permit_columns:
            self.permits_tree.heading(col, text=col)
            self.permits_tree.column(col, width=110, anchor="center")
        self.permits_tree.column("Name", width=160, anchor="w")
        self.permits_tree.column("Email", width=190, anchor="w")
        self.permits_tree.column("Car park", width=220, anchor="w")
        self.permits_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.permits_tree.yview)
        self.permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        review = ttk.Frame(table_frame)
        review.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        for idx in range(9):
            review.columnconfigure(idx, weight=1 if idx in {3, 5, 6} else 0)

        ttk.Label(review, text="Review status").grid(row=0, column=0, sticky="w")
        self.permit_status_var = tk.StringVar(value="Awaiting SMT Approval")
        ttk.Combobox(review, textvariable=self.permit_status_var, values=PERMIT_APP_STATUSES, state="readonly", width=22).grid(row=0, column=1, sticky="w", padx=(8, 12))

        ttk.Label(review, text="Reviewer").grid(row=0, column=2, sticky="w")
        self.permit_reviewer_var = tk.StringVar()
        ttk.Entry(review, textvariable=self.permit_reviewer_var, width=16).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(review, text="Notes").grid(row=0, column=4, sticky="w")
        self.permit_review_notes = tk.StringVar()
        ttk.Entry(review, textvariable=self.permit_review_notes).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        ttk.Button(review, text="Update selected", command=self.update_selected_permit_status).grid(row=0, column=6, sticky="ew")
        ttk.Button(review, text="View selected", command=self.show_selected_permit_details).grid(row=0, column=7, sticky="ew", padx=(8, 12))
        ttk.Button(review, text="Refresh", command=self.refresh_permits).grid(row=0, column=8, sticky="ew")

        issue_frame = ttk.Frame(table_frame)
        issue_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        for idx in range(8):
            issue_frame.columnconfigure(idx, weight=1 if idx in {1, 3, 5} else 0)

        ttk.Label(issue_frame, text="Issue permit kind").grid(row=0, column=0, sticky="w")
        self.issue_permit_kind_var = tk.StringVar(value="Standard")
        ttk.Combobox(issue_frame, textvariable=self.issue_permit_kind_var, values=PERMIT_KIND_OPTIONS, state="readonly", width=18).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        ttk.Label(issue_frame, text="Scope").grid(row=0, column=2, sticky="w")
        self.issue_scope_var = tk.StringVar(value="")
        ttk.Entry(issue_frame, textvariable=self.issue_scope_var).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(issue_frame, text="Expiry").grid(row=0, column=4, sticky="w")
        self.issue_expiry_var = tk.StringVar(value=default_expiry_str())
        ttk.Entry(issue_frame, textvariable=self.issue_expiry_var, width=14).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        self.issue_collection_var = tk.StringVar(value="Old Sessions House reception")
        ttk.Combobox(issue_frame, textvariable=self.issue_collection_var, values=COLLECTION_LOCATIONS, state="readonly", width=24).grid(row=0, column=6, sticky="ew", padx=(0, 12))

        ttk.Button(issue_frame, text="Issue from selected approved application", command=self.issue_selected_permit).grid(row=0, column=7, sticky="ew")

    # ------------------------------
    # Issued permits tab
    # ------------------------------
    def build_issued_permits_tab(self):
        self.issued_permits_tab.columnconfigure(0, weight=1)
        self.issued_permits_tab.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(self.issued_permits_tab, text="Issued permits", padding=8)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("ID", "Permit No", "Holder", "Kind", "Scope", "Reg 1", "Reg 2", "Issued", "Expiry", "Status")
        self.issued_permits_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)
        for col in columns:
            self.issued_permits_tree.heading(col, text=col)
            self.issued_permits_tree.column(col, width=120, anchor="center")
        self.issued_permits_tree.column("Holder", width=170, anchor="w")
        self.issued_permits_tree.column("Permit No", width=150, anchor="w")
        self.issued_permits_tree.column("Scope", width=150, anchor="w")
        self.issued_permits_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.issued_permits_tree.yview)
        self.issued_permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        controls = ttk.Frame(table_frame)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        for idx in range(11):
            controls.columnconfigure(idx, weight=1 if idx in {1, 3, 5} else 0)

        ttk.Label(controls, text="Status").grid(row=0, column=0, sticky="w")
        self.issued_status_var = tk.StringVar(value="Collected")
        ttk.Combobox(controls, textvariable=self.issued_status_var, values=ISSUED_PERMIT_STATUSES, state="readonly", width=22).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="Notes").grid(row=0, column=2, sticky="w")
        self.issued_notes_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.issued_notes_var).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="Replacement fee").grid(row=0, column=4, sticky="w")
        self.replacement_fee_var = tk.StringVar(value="0")
        ttk.Entry(controls, textvariable=self.replacement_fee_var, width=8).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        ttk.Button(controls, text="Update selected", command=self.update_selected_issued_permit).grid(row=0, column=6, sticky="ew")
        ttk.Button(controls, text="View selected", command=self.show_selected_issued_permit).grid(row=0, column=7, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="New reg 1").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.new_reg1_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.new_reg1_var).grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=(8, 0))

        ttk.Label(controls, text="New reg 2").grid(row=1, column=2, sticky="w", pady=(8, 0))
        self.new_reg2_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.new_reg2_var).grid(row=1, column=3, sticky="ew", padx=(8, 12), pady=(8, 0))

        ttk.Button(controls, text="Update vehicle details", command=self.update_selected_issued_permit_regs).grid(row=1, column=4, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(controls, text="Refresh", command=self.refresh_issued_permits).grid(row=1, column=6, sticky="ew", pady=(8, 0))

    # ------------------------------
    # Visitor bookings tab
    # ------------------------------
    def build_visitors_tab(self):
        self.visitors_tab.columnconfigure(1, weight=1)
        self.visitors_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.visitors_tab, text="New visitor booking", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(self.visitors_tab, text="Visitor bookings", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.visitor_vars = {
            "visitor_name": tk.StringVar(),
            "host_name": tk.StringVar(),
            "host_department": tk.StringVar(),
            "email": tk.StringVar(),
            "vehicle_reg": tk.StringVar(),
            "visit_date": tk.StringVar(value=today_str()),
            "car_park": tk.StringVar(),
            "space_required": tk.StringVar(value="1"),
            "notes": tk.StringVar(),
        }
        self.visitor_booked_advance_var = tk.BooleanVar(value=True)
        self.visitor_permit_advance_var = tk.BooleanVar(value=True)

        self.build_form_field(form, "Visitor name", 0, variable=self.visitor_vars["visitor_name"])
        self.build_form_field(form, "Host name", 1, variable=self.visitor_vars["host_name"])
        self.build_form_field(form, "Host department", 2, variable=self.visitor_vars["host_department"])
        self.build_form_field(form, "Email", 3, variable=self.visitor_vars["email"])
        self.build_form_field(form, "Vehicle reg", 4, variable=self.visitor_vars["vehicle_reg"])
        self.build_form_field(form, "Visit date", 5, variable=self.visitor_vars["visit_date"])
        self.build_form_field(form, "Car park", 6, widget="combo", variable=self.visitor_vars["car_park"], values=self.car_park_choices)
        self.build_form_field(form, "Spaces required", 7, variable=self.visitor_vars["space_required"])
        self.build_form_field(form, "Notes", 8, variable=self.visitor_vars["notes"])

        ttk.Checkbutton(form, text="Booked in advance", variable=self.visitor_booked_advance_var).grid(row=9, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Checkbutton(form, text="Permit issued in advance", variable=self.visitor_permit_advance_var).grid(row=10, column=0, columnspan=2, sticky="w")

        ttk.Button(form, text="Save booking", command=self.save_visitor_booking).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.visitor_vars, keep={"visit_date": today_str(), "space_required": "1"})).grid(row=12, column=0, columnspan=2, sticky="ew")

        columns = ("ID", "Visitor", "Host", "Vehicle reg", "Visit date", "Spaces", "Car park", "Status")
        self.visitors_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.visitors_tree.heading(col, text=col)
            self.visitors_tree.column(col, width=120, anchor="center")
        self.visitors_tree.column("Visitor", width=160, anchor="w")
        self.visitors_tree.column("Host", width=160, anchor="w")
        self.visitors_tree.column("Car park", width=220, anchor="w")
        self.visitors_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.visitors_tree.yview)
        self.visitors_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(table_frame, text="Refresh", command=self.refresh_visitors).grid(row=1, column=0, sticky="e", pady=(8, 0))

    # ------------------------------
    # Reservations tab
    # ------------------------------
    def build_reservations_tab(self):
        self.reservations_tab.columnconfigure(1, weight=1)
        self.reservations_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.reservations_tab, text="New reservation / prior consent", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(self.reservations_tab, text="Reservations", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.reservation_vars = {
            "reserved_for": tk.StringVar(),
            "reservation_type": tk.StringVar(value="Event"),
            "contact_name": tk.StringVar(),
            "vehicle_reg": tk.StringVar(),
            "car_park": tk.StringVar(),
            "bay_count": tk.StringVar(value="1"),
            "start_date": tk.StringVar(value=today_str()),
            "end_date": tk.StringVar(value=today_str()),
            "approved_by": tk.StringVar(),
            "notes": tk.StringVar(),
        }

        self.build_form_field(form, "Reserved for", 0, variable=self.reservation_vars["reserved_for"])
        self.build_form_field(form, "Reservation type", 1, widget="combo", variable=self.reservation_vars["reservation_type"], values=["Event", "Contractor", "Guest", "VIP", "Short Stay", "Other"])
        self.build_form_field(form, "Contact name", 2, variable=self.reservation_vars["contact_name"])
        self.build_form_field(form, "Vehicle reg", 3, variable=self.reservation_vars["vehicle_reg"])
        self.build_form_field(form, "Car park", 4, widget="combo", variable=self.reservation_vars["car_park"], values=self.car_park_choices)
        self.build_form_field(form, "Bay count", 5, variable=self.reservation_vars["bay_count"])
        self.build_form_field(form, "Start date", 6, variable=self.reservation_vars["start_date"])
        self.build_form_field(form, "End date", 7, variable=self.reservation_vars["end_date"])
        self.build_form_field(form, "Approved / consent by", 8, variable=self.reservation_vars["approved_by"])
        self.build_form_field(form, "Notes", 9, variable=self.reservation_vars["notes"])

        ttk.Button(form, text="Save reservation", command=self.save_reservation).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.reservation_vars, keep={"reservation_type": "Event", "bay_count": "1", "start_date": today_str(), "end_date": today_str()})).grid(row=11, column=0, columnspan=2, sticky="ew")

        columns = ("ID", "Reserved for", "Type", "Contact", "Vehicle reg", "Start", "End", "Bays", "Car park", "Status")
        self.reservations_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.reservations_tree.heading(col, text=col)
            self.reservations_tree.column(col, width=110, anchor="center")
        self.reservations_tree.column("Reserved for", width=160, anchor="w")
        self.reservations_tree.column("Contact", width=150, anchor="w")
        self.reservations_tree.column("Car park", width=220, anchor="w")
        self.reservations_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.reservations_tree.yview)
        self.reservations_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(table_frame, text="Refresh", command=self.refresh_reservations).grid(row=1, column=0, sticky="e", pady=(8, 0))

    # ------------------------------
    # Temporary permits tab
    # ------------------------------
    def build_temp_permits_tab(self):
        self.temp_permits_tab.columnconfigure(1, weight=1)
        self.temp_permits_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.temp_permits_tab, text="New temporary / day / EV permit", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(self.temp_permits_tab, text="Temporary permits", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.temp_vars = {
            "permit_holder": tk.StringVar(),
            "vehicle_reg": tk.StringVar(),
            "permit_type": tk.StringVar(value="Temporary"),
            "start_date": tk.StringVar(value=today_str()),
            "end_date": tk.StringVar(value=today_str()),
            "approved_by": tk.StringVar(),
            "reason_recorded": tk.StringVar(),
            "notes": tk.StringVar(),
        }

        self.build_form_field(form, "Permit holder", 0, variable=self.temp_vars["permit_holder"])
        self.build_form_field(form, "Vehicle reg", 1, variable=self.temp_vars["vehicle_reg"])
        self.build_form_field(form, "Permit type", 2, widget="combo", variable=self.temp_vars["permit_type"], values=TEMP_PERMIT_OPTIONS)
        self.build_form_field(form, "Start date", 3, variable=self.temp_vars["start_date"])
        self.build_form_field(form, "End date", 4, variable=self.temp_vars["end_date"])
        self.build_form_field(form, "Approved by", 5, variable=self.temp_vars["approved_by"])
        self.build_form_field(form, "Reason recorded", 6, variable=self.temp_vars["reason_recorded"])
        self.build_form_field(form, "Notes", 7, variable=self.temp_vars["notes"])

        ttk.Button(form, text="Save temporary permit", command=self.save_temporary_permit).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.temp_vars, keep={"permit_type": "Temporary", "start_date": today_str(), "end_date": today_str()})).grid(row=9, column=0, columnspan=2, sticky="ew")

        columns = ("ID", "Holder", "Vehicle reg", "Type", "Start", "End", "Status")
        self.temp_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.temp_tree.heading(col, text=col)
            self.temp_tree.column(col, width=130, anchor="center")
        self.temp_tree.column("Holder", width=180, anchor="w")
        self.temp_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.temp_tree.yview)
        self.temp_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(table_frame, text="Refresh", command=self.refresh_temp_permits).grid(row=1, column=0, sticky="e", pady=(8, 0))

    # ------------------------------
    # Patrol checker tab
    # ------------------------------
    def build_checker_tab(self):
        self.checker_tab.columnconfigure(0, weight=1)
        self.checker_tab.rowconfigure(1, weight=1)

        controls = ttk.LabelFrame(self.checker_tab, text="Patrol check", padding=12)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(3, weight=1)

        self.check_reg_var = tk.StringVar()
        self.check_date_var = tk.StringVar(value=today_str())

        ttk.Label(controls, text="Vehicle reg").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.check_reg_var, width=20).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Label(controls, text="Check date").grid(row=0, column=2, sticky="w")
        ttk.Entry(controls, textvariable=self.check_date_var, width=14).grid(row=0, column=3, sticky="w", padx=(8, 12))
        ttk.Button(controls, text="Check vehicle", command=self.check_vehicle).grid(row=0, column=4, sticky="e")

        result_frame = ttk.LabelFrame(self.checker_tab, text="Result", padding=8)
        result_frame.grid(row=1, column=0, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.check_result = tk.Text(result_frame, wrap="word", font=("Consolas", 10))
        self.check_result.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.check_result.yview)
        self.check_result.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

    # ------------------------------
    # Penalties tab
    # ------------------------------
    def build_penalties_tab(self):
        self.penalties_tab.columnconfigure(1, weight=1)
        self.penalties_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.penalties_tab, text="New penalty notice", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(self.penalties_tab, text="Penalty notices", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.penalty_vars = {
            "vehicle_reg": tk.StringVar(),
            "reason": tk.StringVar(value="No valid permit"),
            "location": tk.StringVar(),
            "issued_by": tk.StringVar(),
            "external_status": tk.StringVar(value="Sent to Workflow Dynamics"),
            "appeal_status": tk.StringVar(value="No Appeal"),
            "notes": tk.StringVar(),
        }

        self.build_form_field(form, "Vehicle reg", 0, variable=self.penalty_vars["vehicle_reg"])
        self.build_form_field(form, "Reason", 1, widget="combo", variable=self.penalty_vars["reason"], values=["No valid permit", "Parked in wrong bay", "Overstayed", "Unauthorised visitor parking", "Incorrect bay use", "Other"])
        self.build_form_field(form, "Location", 2, variable=self.penalty_vars["location"])
        self.build_form_field(form, "Issued by", 3, variable=self.penalty_vars["issued_by"])
        self.build_form_field(form, "External status", 4, widget="combo", variable=self.penalty_vars["external_status"], values=["Sent to Workflow Dynamics", "Draft", "Cancelled", "Closed"])
        self.build_form_field(form, "Appeal status", 5, widget="combo", variable=self.penalty_vars["appeal_status"], values=["No Appeal", "Under Review", "Upheld", "Cancelled"])
        self.build_form_field(form, "Notes", 6, variable=self.penalty_vars["notes"])

        ttk.Button(form, text="Save penalty notice", command=self.save_penalty).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.penalty_vars, keep={"reason": "No valid permit", "external_status": "Sent to Workflow Dynamics", "appeal_status": "No Appeal"})).grid(row=8, column=0, columnspan=2, sticky="ew")

        columns = ("ID", "Vehicle reg", "Reason", "Location", "Issued by", "External status", "Appeal status", "Issued at")
        self.penalties_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.penalties_tree.heading(col, text=col)
            self.penalties_tree.column(col, width=120, anchor="center")
        self.penalties_tree.column("Reason", width=170, anchor="w")
        self.penalties_tree.column("Location", width=150, anchor="w")
        self.penalties_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.penalties_tree.yview)
        self.penalties_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(table_frame, text="Refresh", command=self.refresh_penalties).grid(row=1, column=0, sticky="e", pady=(8, 0))

    # ------------------------------
    # Shared small UI helpers
    # ------------------------------
    def build_form_field(self, parent, label, row, variable, widget="entry", values=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 8))
        if widget == "combo":
            control = ttk.Combobox(parent, textvariable=variable, values=values or [], state="readonly", width=34)
        else:
            control = ttk.Entry(parent, textvariable=variable, width=37)
        control.grid(row=row, column=1, sticky="ew", pady=3)
        parent.columnconfigure(1, weight=1)
        return control

    def clear_vars(self, variables, keep=None):
        keep = keep or {}
        for key, var in variables.items():
            var.set(keep.get(key, ""))

    def require(self, value, label):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError(f"{label} is required.")
        return cleaned

    def selected_tree_id(self, tree):
        selected = tree.selection()
        return tree.item(selected[0], "values")[0] if selected else None

    def replace_tree_data(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=tuple(row))

    # ------------------------------
    # Refresh logic
    # ------------------------------
    def refresh_all(self):
        self.car_park_choices = self.db.car_park_options()
        self.refresh_dashboard()
        self.refresh_permits()
        self.refresh_issued_permits()
        self.refresh_visitors()
        self.refresh_reservations()
        self.refresh_temp_permits()
        self.refresh_penalties()

    def refresh_dashboard(self):
        counts = self.db.dashboard_counts()
        for key, label in self.kpi_labels.items():
            label.config(text=str(counts.get(key, 0)))

        for item in self.carparks_tree.get_children():
            self.carparks_tree.delete(item)
        for row in self.db.fetch_car_parks():
            self.carparks_tree.insert(
                "",
                "end",
                values=(row["campus"], row["name"], row["standard_bays"], row["visitor_bays"], row["electric_charging"], row["disabled_bays"], row["total_bays"]),
            )

    def refresh_permits(self):
        self.replace_tree_data(self.permits_tree, self.db.list_permit_applications())

    def refresh_issued_permits(self):
        self.replace_tree_data(self.issued_permits_tree, self.db.list_issued_permits())

    def refresh_visitors(self):
        self.replace_tree_data(self.visitors_tree, self.db.list_visitor_bookings())

    def refresh_reservations(self):
        self.replace_tree_data(self.reservations_tree, self.db.list_reservations())

    def refresh_temp_permits(self):
        self.replace_tree_data(self.temp_tree, self.db.list_temporary_permits())

    def refresh_penalties(self):
        self.replace_tree_data(self.penalties_tree, self.db.list_penalties())

    def start_auto_refresh(self):
        # This keeps the admin side updated if someone is filling out the separate application form at the same time.
        self.after(10000, self.auto_refresh_tick)

    def auto_refresh_tick(self):
        try:
            self.refresh_dashboard()
            self.refresh_permits()
            self.refresh_issued_permits()
        finally:
            self.after(10000, self.auto_refresh_tick)

    # ------------------------------
    # Permit application review actions
    # ------------------------------
    def update_selected_permit_status(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select a permit application first.")
                return

            reviewer = self.require(self.permit_reviewer_var.get(), "Reviewer")
            self.db.update_permit_status(permit_id, self.permit_status_var.get(), reviewer, self.permit_review_notes.get().strip())
            self.refresh_all()
            messagebox.showinfo("Updated", "Permit status updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def issue_selected_permit(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an approved application first.")
                return

            expiry = ensure_date(self.issue_expiry_var.get(), "Issue expiry", allow_blank=False)
            self.db.issue_permit_from_application(
                permit_id,
                self.issue_permit_kind_var.get().strip(),
                self.issue_scope_var.get().strip(),
                expiry,
                self.issue_collection_var.get().strip(),
                self.permit_review_notes.get().strip(),
            )
            self.refresh_all()
            messagebox.showinfo("Issued", "Permit created and marked ready for collection.")
        except Exception as exc:
            messagebox.showerror("Could not issue", str(exc))

    def show_text_window(self, title, text):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("760x640")
        top.transient(self)

        frame = ttk.Frame(top, padding=12)
        frame.pack(fill="both", expand=True)

        text_box = tk.Text(frame, wrap="word", font=("Consolas", 10))
        text_box.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
        scroll.pack(side="right", fill="y")
        text_box.configure(yscrollcommand=scroll.set)
        text_box.insert("1.0", text)
        text_box.configure(state="disabled")

    def show_selected_permit_details(self):
        permit_id = self.selected_tree_id(self.permits_tree)
        if not permit_id:
            messagebox.showwarning("No selection", "Please select an application first.")
            return

        record = self.db.get_permit_application(permit_id)
        details = [
            f"Application #{record['id']}",
            f"Applicant: {record['full_name']} ({record['applicant_type']})",
            f"Campus: {record['campus']}",
            f"Email: {record['email']}",
            f"Department: {record['department'] or '-'}",
            f"Payroll / University ID: {record['payroll_number'] or record['university_id'] or '-'}",
            f"Contact number: {record['contact_number'] or '-'}",
            f"Employment type: {record['employment_type'] or '-'}",
            f"Home postcode: {record['home_postcode'] or '-'}",
            f"Vehicle reg 1: {record['vehicle_reg']}",
            f"Vehicle reg 2: {record['secondary_vehicle_reg'] or '-'}",
            f"Desired car park: {record['car_park_name'] or '-'}",
            f"Requested dates: {record['valid_from'] or '-'} to {record['valid_to'] or '-'}",
            "",
            "Eligibility flags",
            f"  Blue Badge: {as_yes_no(bool(record['blue_badge']))}",
            f"  Mobility / health condition: {as_yes_no(bool(record['mobility_need']))}",
            f"  Registered carer: {as_yes_no(bool(record['registered_carer']))}",
            f"  Child 11 or under: {as_yes_no(bool(record['child_under_11']))}",
            f"  Essential business user: {as_yes_no(bool(record['essential_business_user']))}",
            f"  Business travel trips/week: {record['business_travel_trips']}",
            f"  Business insurance: {as_yes_no(bool(record['business_insurance']))}",
            f"  Friday-only requested: {as_yes_no(bool(record['friday_only_requested']))}",
            "",
            f"Reason: {record['reason'] or '-'}",
            f"Accessibility / health notes: {record['accessibility_needs'] or '-'}",
            f"Evidence summary: {record['evidence_summary'] or '-'}",
            f"Planned days: {record['planned_days'] or '-'}",
            f"Permit scope: {record['permit_scope'] or '-'}",
            f"Collection location: {record['collection_location'] or '-'}",
            "",
            "Authorisation",
            f"Status: {record['status']}",
            f"HoD recommendation: {record['head_recommendation']} by {record['head_recommended_by'] or '-'} on {record['head_recommendation_date'] or '-'}",
            f"SMT decision: {record['smt_decision']} by {record['smt_decided_by'] or '-'} on {record['smt_decision_date'] or '-'}",
            f"Appeal status: {record['appeal_status']}",
            f"Reviewer notes: {record['reviewer_notes'] or '-'}",
        ]
        self.show_text_window(f"Permit application #{record['id']}", "\n".join(details))

    # ------------------------------
    # Visitor / reservation / temp / penalty saves
    # ------------------------------
    def save_visitor_booking(self):
        try:
            data = {
                "visitor_name": self.require(self.visitor_vars["visitor_name"].get(), "Visitor name"),
                "host_name": self.require(self.visitor_vars["host_name"].get(), "Host name"),
                "host_department": self.visitor_vars["host_department"].get().strip(),
                "email": self.require(self.visitor_vars["email"].get(), "Email"),
                "vehicle_reg": normalise_reg(self.require(self.visitor_vars["vehicle_reg"].get(), "Vehicle reg")),
                "visit_date": ensure_date(self.visitor_vars["visit_date"].get(), "Visit date", allow_blank=False),
                "car_park_id": parse_car_park_id(self.visitor_vars["car_park"].get()),
                "space_required": int(self.visitor_vars["space_required"].get().strip() or "1"),
                "notes": self.visitor_vars["notes"].get().strip(),
                "booked_in_advance": self.visitor_booked_advance_var.get(),
                "permit_issued_in_advance": self.visitor_permit_advance_var.get(),
            }
            self.db.add_visitor_booking(data)
            self.refresh_all()
            self.clear_vars(self.visitor_vars, keep={"visit_date": today_str(), "space_required": "1"})
            self.visitor_booked_advance_var.set(True)
            self.visitor_permit_advance_var.set(True)
            messagebox.showinfo("Saved", "Visitor booking saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_reservation(self):
        try:
            data = {
                "reserved_for": self.require(self.reservation_vars["reserved_for"].get(), "Reserved for"),
                "reservation_type": self.reservation_vars["reservation_type"].get().strip(),
                "contact_name": self.require(self.reservation_vars["contact_name"].get(), "Contact name"),
                "vehicle_reg": normalise_reg(self.reservation_vars["vehicle_reg"].get().strip()) if self.reservation_vars["vehicle_reg"].get().strip() else "",
                "car_park_id": parse_car_park_id(self.reservation_vars["car_park"].get()),
                "bay_count": int(self.reservation_vars["bay_count"].get().strip() or "1"),
                "start_date": ensure_date(self.reservation_vars["start_date"].get(), "Start date", allow_blank=False),
                "end_date": ensure_date(self.reservation_vars["end_date"].get(), "End date", allow_blank=False),
                "approved_by": self.reservation_vars["approved_by"].get().strip(),
                "notes": self.reservation_vars["notes"].get().strip(),
            }
            self.db.add_reservation(data)
            self.refresh_all()
            self.clear_vars(self.reservation_vars, keep={"reservation_type": "Event", "bay_count": "1", "start_date": today_str(), "end_date": today_str()})
            messagebox.showinfo("Saved", "Reservation saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_temporary_permit(self):
        try:
            data = {
                "permit_holder": self.require(self.temp_vars["permit_holder"].get(), "Permit holder"),
                "vehicle_reg": normalise_reg(self.require(self.temp_vars["vehicle_reg"].get(), "Vehicle reg")),
                "permit_type": self.temp_vars["permit_type"].get().strip(),
                "start_date": ensure_date(self.temp_vars["start_date"].get(), "Start date", allow_blank=False),
                "end_date": ensure_date(self.temp_vars["end_date"].get(), "End date", allow_blank=False),
                "approved_by": self.temp_vars["approved_by"].get().strip(),
                "reason_recorded": self.temp_vars["reason_recorded"].get().strip(),
                "notes": self.temp_vars["notes"].get().strip(),
            }
            self.db.add_temporary_permit(data)
            self.refresh_all()
            self.clear_vars(self.temp_vars, keep={"permit_type": "Temporary", "start_date": today_str(), "end_date": today_str()})
            messagebox.showinfo("Saved", "Temporary/day permit saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_penalty(self):
        try:
            data = {
                "vehicle_reg": normalise_reg(self.require(self.penalty_vars["vehicle_reg"].get(), "Vehicle reg")),
                "reason": self.penalty_vars["reason"].get().strip(),
                "location": self.require(self.penalty_vars["location"].get(), "Location"),
                "issued_by": self.require(self.penalty_vars["issued_by"].get(), "Issued by"),
                "external_status": self.penalty_vars["external_status"].get().strip(),
                "appeal_status": self.penalty_vars["appeal_status"].get().strip(),
                "notes": self.penalty_vars["notes"].get().strip(),
            }
            self.db.add_penalty(data)
            self.refresh_all()
            self.clear_vars(self.penalty_vars, keep={"reason": "No valid permit", "external_status": "Sent to Workflow Dynamics", "appeal_status": "No Appeal"})
            messagebox.showinfo("Saved", "Penalty notice saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    # ------------------------------
    # Issued permit actions
    # ------------------------------
    def update_selected_issued_permit(self):
        try:
            permit_id = self.selected_tree_id(self.issued_permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an issued permit first.")
                return

            self.db.update_issued_permit(
                permit_id,
                self.issued_status_var.get(),
                self.issued_notes_var.get().strip(),
                float(self.replacement_fee_var.get().strip() or "0"),
            )
            self.refresh_all()
            messagebox.showinfo("Updated", "Issued permit updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def update_selected_issued_permit_regs(self):
        try:
            permit_id = self.selected_tree_id(self.issued_permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an issued permit first.")
                return

            self.db.update_issued_permit_regs(
                permit_id,
                self.require(self.new_reg1_var.get(), "New reg 1"),
                self.new_reg2_var.get().strip(),
            )
            self.refresh_all()
            self.new_reg1_var.set("")
            self.new_reg2_var.set("")
            messagebox.showinfo("Updated", "Permit vehicle details updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def show_selected_issued_permit(self):
        permit_id = self.selected_tree_id(self.issued_permits_tree)
        if not permit_id:
            messagebox.showwarning("No selection", "Please select an issued permit first.")
            return

        record = self.db.get_issued_permit(permit_id)
        details = [
            f"Issued Permit #{record['id']}",
            f"Permit number: {record['permit_number']}",
            f"Holder: {record['holder_name']}",
            f"Kind: {record['permit_kind']}",
            f"Scope: {record['campus_scope']}",
            f"Vehicle reg 1: {record['vehicle_reg_primary']}",
            f"Vehicle reg 2: {record['vehicle_reg_secondary'] or '-'}",
            f"Issued date: {record['issued_date']}",
            f"Expiry: {record['expiry_date']}",
            f"Collection location: {record['collection_location'] or '-'}",
            f"Status: {record['status']}",
            f"Replacement fee due: £{record['replacement_fee_due']:.2f}",
            f"Return received: {as_yes_no(bool(record['return_received']))}",
            f"Cancelled at: {record['cancelled_at'] or '-'}",
            f"Notes: {record['notes'] or '-'}",
        ]
        self.show_text_window(f"Issued permit #{record['id']}", "\n".join(details))

    # ------------------------------
    # Patrol check action
    # ------------------------------
    def check_vehicle(self):
        try:
            reg = normalise_reg(self.require(self.check_reg_var.get(), "Vehicle reg"))
            check_date = ensure_date(self.check_date_var.get(), "Check date", allow_blank=False)
            result = self.db.check_vehicle(reg, check_date)

            lines = [f"Vehicle check for {reg}", f"Date: {check_date}", "-" * 72]
            weekday_name = parse_date(check_date).strftime("%A")

            valid_issued = [permit for permit in result["issued_permits"] if not (permit["permit_kind"] == "Friday Only" and weekday_name != "Friday")]
            if valid_issued:
                lines.append("Issued permit(s) found")
                for permit in valid_issued:
                    lines.append(f"• {permit['permit_number']} | {permit['permit_kind']} | {permit['campus_scope']} | {permit['issued_date']} to {permit['expiry_date']} | status {permit['status']}")
                lines.append("")
            else:
                lines.extend(["No active issued permit found for that date.", ""])

            if result["temporary_permit"]:
                temp = result["temporary_permit"]
                lines.extend(["Temporary / day permit found", f"Holder: {temp['permit_holder']}", f"Type: {temp['permit_type']}", f"Valid: {temp['start_date']} to {temp['end_date']}", ""])

            if result["visitor"]:
                visitor = result["visitor"]
                lines.extend(["Visitor booking found", f"Visitor: {visitor['visitor_name']}", f"Host: {visitor['host_name']}", f"Car park: {visitor['car_park']}", ""])

            if result["reservation"]:
                reservation = result["reservation"]
                lines.extend(["Reservation / prior consent found", f"Reserved for: {reservation['reserved_for']}", f"Type: {reservation['reservation_type']}", f"Contact: {reservation['contact_name']}", f"Car park: {reservation['car_park']}", f"Dates: {reservation['start_date']} to {reservation['end_date']}", ""])

            if not any([valid_issued, result["temporary_permit"], result["visitor"], result["reservation"]]):
                lines.extend(["No current permit, temporary/day permit, visitor booking or reservation found.", "This vehicle may need further checking by patrol staff.", ""])

            lines.append("Recent penalty history")
            if result["penalties"]:
                for penalty in result["penalties"]:
                    lines.append(f"• #{penalty['id']} | {penalty['reason']} | {penalty['location']} | {penalty['issued_at']}")
            else:
                lines.append("• No previous penalty notices recorded.")

            self.check_result.delete("1.0", tk.END)
            self.check_result.insert("1.0", "\n".join(lines))
        except Exception as exc:
            messagebox.showerror("Could not check vehicle", str(exc))


if __name__ == "__main__":
    app = CarParkAdminDashboard()
    app.mainloop()
