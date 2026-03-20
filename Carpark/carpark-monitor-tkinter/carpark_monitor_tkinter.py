
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).with_name("carpark_monitor.db")

CAR_PARK_SEED = [
    {"campus": "Canterbury", "name": "Verena Holmes Undercroft", "standard_bays": 12, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 10, "department_bays": 0, "total_bays": 25},
    {"campus": "Canterbury", "name": "Black Car Park (Verena Holmes)", "standard_bays": 63, "visitor_bays": 2, "short_stay_bays": 0, "electric_charging": 10, "disabled_bays": 5, "contractor_bays": 9, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 89},
    {"campus": "Canterbury", "name": "Vernon Place", "standard_bays": 7, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 8},
    {"campus": "Canterbury", "name": "Red Car Park (North Holmes Road)", "standard_bays": 29, "visitor_bays": 4, "short_stay_bays": 2, "electric_charging": 2, "disabled_bays": 7, "contractor_bays": 0, "motorcycle_bays": 1, "department_bays": 8, "total_bays": 53},
    {"campus": "Canterbury", "name": "Green Car Park (Governor's Hse)", "standard_bays": 32, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 33},
    {"campus": "Canterbury", "name": "St Martins Priory", "standard_bays": 22, "visitor_bays": 8, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 5, "total_bays": 37},
    {"campus": "Canterbury", "name": "Augustine House", "standard_bays": 5, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 2, "total_bays": 7},
    {"campus": "Canterbury", "name": "St. George's Student Union", "standard_bays": 0, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 2},
    {"campus": "Canterbury", "name": "Yellow Car Park (St. Gregory's) approx", "standard_bays": 41, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 41},
    {"campus": "Canterbury", "name": "TOSH Visitors Car Park", "standard_bays": 0, "visitor_bays": 15, "short_stay_bays": 1, "electric_charging": 2, "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 2, "total_bays": 21},
    {"campus": "Canterbury", "name": "Mauve Car Park (TOSH)", "standard_bays": 9, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 9},
    {"campus": "Canterbury", "name": "Grey Car Park (Prison)", "standard_bays": 44, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 6, "total_bays": 53},
    {"campus": "Canterbury", "name": "Sports Centre", "standard_bays": 7, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 10},
    {"campus": "Medway", "name": "Rowan Williams Court", "standard_bays": 121, "visitor_bays": 30, "short_stay_bays": 0, "electric_charging": 2, "disabled_bays": 4, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 4, "total_bays": 157},
    {"campus": "Medway", "name": "Cathedral Court", "standard_bays": 88, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 1, "total_bays": 89},
    {"campus": "Medway", "name": "North Road", "standard_bays": 15, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 0, "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 15},
]


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.initialise()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialise(self):
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS car_parks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campus TEXT NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    standard_bays INTEGER NOT NULL DEFAULT 0,
                    visitor_bays INTEGER NOT NULL DEFAULT 0,
                    short_stay_bays INTEGER NOT NULL DEFAULT 0,
                    electric_charging INTEGER NOT NULL DEFAULT 0,
                    disabled_bays INTEGER NOT NULL DEFAULT 0,
                    contractor_bays INTEGER NOT NULL DEFAULT 0,
                    motorcycle_bays INTEGER NOT NULL DEFAULT 0,
                    department_bays INTEGER NOT NULL DEFAULT 0,
                    total_bays INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS permit_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_type TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    university_id TEXT,
                    email TEXT NOT NULL,
                    vehicle_reg TEXT NOT NULL,
                    reason TEXT,
                    accessibility_needs TEXT,
                    distance_km REAL,
                    desired_car_park_id INTEGER,
                    valid_from TEXT,
                    valid_to TEXT,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    reviewer_notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (desired_car_park_id) REFERENCES car_parks(id)
                );

                CREATE TABLE IF NOT EXISTS visitor_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visitor_name TEXT NOT NULL,
                    host_name TEXT NOT NULL,
                    host_department TEXT,
                    email TEXT NOT NULL,
                    vehicle_reg TEXT NOT NULL,
                    visit_date TEXT NOT NULL,
                    car_park_id INTEGER,
                    space_required INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'Booked',
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (car_park_id) REFERENCES car_parks(id)
                );

                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reserved_for TEXT NOT NULL,
                    reservation_type TEXT NOT NULL,
                    contact_name TEXT NOT NULL,
                    vehicle_reg TEXT,
                    car_park_id INTEGER,
                    bay_count INTEGER NOT NULL DEFAULT 1,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (car_park_id) REFERENCES car_parks(id)
                );

                CREATE TABLE IF NOT EXISTS temporary_permits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    permit_holder TEXT NOT NULL,
                    vehicle_reg TEXT NOT NULL,
                    permit_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    notes TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS penalties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_reg TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    location TEXT NOT NULL,
                    issued_by TEXT NOT NULL,
                    external_status TEXT NOT NULL DEFAULT 'Sent to Workflow Dynamics',
                    appeal_status TEXT NOT NULL DEFAULT 'No Appeal',
                    notes TEXT,
                    issued_at TEXT NOT NULL
                );
                """
            )
            self.seed_car_parks(conn)

    def seed_car_parks(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM car_parks").fetchone()[0]
        if count:
            return
        for park in CAR_PARK_SEED:
            conn.execute(
                """
                INSERT INTO car_parks (
                    campus, name, standard_bays, visitor_bays, short_stay_bays,
                    electric_charging, disabled_bays, contractor_bays, motorcycle_bays,
                    department_bays, total_bays
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    park["campus"],
                    park["name"],
                    park["standard_bays"],
                    park["visitor_bays"],
                    park["short_stay_bays"],
                    park["electric_charging"],
                    park["disabled_bays"],
                    park["contractor_bays"],
                    park["motorcycle_bays"],
                    park["department_bays"],
                    park["total_bays"],
                ),
            )

    def fetch_car_parks(self):
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM car_parks ORDER BY campus, name"
            ).fetchall()

    def car_park_options(self):
        parks = self.fetch_car_parks()
        return [f"{row['id']} - {row['campus']} - {row['name']}" for row in parks]

    def add_permit_application(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO permit_applications (
                    applicant_type, full_name, university_id, email, vehicle_reg,
                    reason, accessibility_needs, distance_km, desired_car_park_id,
                    valid_from, valid_to, status, reviewer_notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["applicant_type"],
                    data["full_name"],
                    data["university_id"],
                    data["email"],
                    data["vehicle_reg"],
                    data["reason"],
                    data["accessibility_needs"],
                    data["distance_km"],
                    data["desired_car_park_id"],
                    data["valid_from"],
                    data["valid_to"],
                    "Pending",
                    "",
                    now_str(),
                ),
            )

    def list_permit_applications(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT p.id, p.applicant_type, p.full_name, p.vehicle_reg, p.email,
                       COALESCE(c.name, '') AS car_park, p.valid_from, p.valid_to,
                       p.status, p.created_at
                FROM permit_applications p
                LEFT JOIN car_parks c ON c.id = p.desired_car_park_id
                ORDER BY p.id DESC
                """
            ).fetchall()

    def update_permit_status(self, permit_id, status, notes):
        with self.connect() as conn:
            conn.execute(
                "UPDATE permit_applications SET status = ?, reviewer_notes = ? WHERE id = ?",
                (status, notes, permit_id),
            )

    def add_visitor_booking(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO visitor_bookings (
                    visitor_name, host_name, host_department, email, vehicle_reg,
                    visit_date, car_park_id, space_required, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["visitor_name"],
                    data["host_name"],
                    data["host_department"],
                    data["email"],
                    data["vehicle_reg"],
                    data["visit_date"],
                    data["car_park_id"],
                    data["space_required"],
                    "Booked",
                    data["notes"],
                    now_str(),
                ),
            )

    def list_visitor_bookings(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT v.id, v.visitor_name, v.host_name, v.vehicle_reg, v.visit_date,
                       v.space_required, COALESCE(c.name, '') AS car_park, v.status
                FROM visitor_bookings v
                LEFT JOIN car_parks c ON c.id = v.car_park_id
                ORDER BY v.visit_date DESC, v.id DESC
                """
            ).fetchall()

    def add_reservation(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO reservations (
                    reserved_for, reservation_type, contact_name, vehicle_reg, car_park_id,
                    bay_count, start_date, end_date, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["reserved_for"],
                    data["reservation_type"],
                    data["contact_name"],
                    data["vehicle_reg"],
                    data["car_park_id"],
                    data["bay_count"],
                    data["start_date"],
                    data["end_date"],
                    "Active",
                    data["notes"],
                    now_str(),
                ),
            )

    def list_reservations(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT r.id, r.reserved_for, r.reservation_type, r.contact_name,
                       r.vehicle_reg, r.start_date, r.end_date, r.bay_count,
                       COALESCE(c.name, '') AS car_park, r.status
                FROM reservations r
                LEFT JOIN car_parks c ON c.id = r.car_park_id
                ORDER BY r.start_date DESC, r.id DESC
                """
            ).fetchall()

    def add_temporary_permit(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO temporary_permits (
                    permit_holder, vehicle_reg, permit_type, start_date, end_date,
                    status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["permit_holder"],
                    data["vehicle_reg"],
                    data["permit_type"],
                    data["start_date"],
                    data["end_date"],
                    "Active",
                    data["notes"],
                    now_str(),
                ),
            )

    def list_temporary_permits(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, permit_holder, vehicle_reg, permit_type, start_date, end_date, status
                FROM temporary_permits
                ORDER BY start_date DESC, id DESC
                """
            ).fetchall()

    def add_penalty(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO penalties (
                    vehicle_reg, reason, location, issued_by, external_status,
                    appeal_status, notes, issued_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["vehicle_reg"],
                    data["reason"],
                    data["location"],
                    data["issued_by"],
                    data["external_status"],
                    data["appeal_status"],
                    data["notes"],
                    now_str(),
                ),
            )

    def list_penalties(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, vehicle_reg, reason, location, issued_by,
                       external_status, appeal_status, issued_at
                FROM penalties
                ORDER BY id DESC
                """
            ).fetchall()

    def dashboard_counts(self):
        with self.connect() as conn:
            return {
                "car_parks": conn.execute("SELECT COUNT(*) FROM car_parks").fetchone()[0],
                "total_spaces": conn.execute("SELECT COALESCE(SUM(total_bays),0) FROM car_parks WHERE campus='Canterbury'").fetchone()[0],
                "pending_permits": conn.execute("SELECT COUNT(*) FROM permit_applications WHERE status='Pending'").fetchone()[0],
                "approved_permits": conn.execute("SELECT COUNT(*) FROM permit_applications WHERE status='Approved'").fetchone()[0],
                "today_visitors": conn.execute("SELECT COUNT(*) FROM visitor_bookings WHERE visit_date = ?", (today_str(),)).fetchone()[0],
                "active_reservations": conn.execute("SELECT COUNT(*) FROM reservations WHERE status='Active' AND start_date <= ? AND end_date >= ?", (today_str(), today_str())).fetchone()[0],
                "active_temporary_permits": conn.execute("SELECT COUNT(*) FROM temporary_permits WHERE status='Active' AND start_date <= ? AND end_date >= ?", (today_str(), today_str())).fetchone()[0],
                "penalties": conn.execute("SELECT COUNT(*) FROM penalties").fetchone()[0],
            }

    def check_vehicle(self, vehicle_reg, check_date):
        with self.connect() as conn:
            permit = conn.execute(
                """
                SELECT full_name, applicant_type, status, valid_from, valid_to
                FROM permit_applications
                WHERE UPPER(vehicle_reg) = UPPER(?)
                  AND status = 'Approved'
                  AND (valid_from IS NULL OR valid_from = '' OR valid_from <= ?)
                  AND (valid_to IS NULL OR valid_to = '' OR valid_to >= ?)
                ORDER BY id DESC LIMIT 1
                """,
                (vehicle_reg, check_date, check_date),
            ).fetchone()

            temp_permit = conn.execute(
                """
                SELECT permit_holder, permit_type, start_date, end_date
                FROM temporary_permits
                WHERE UPPER(vehicle_reg) = UPPER(?)
                  AND status = 'Active'
                  AND start_date <= ?
                  AND end_date >= ?
                ORDER BY id DESC LIMIT 1
                """,
                (vehicle_reg, check_date, check_date),
            ).fetchone()

            visitor = conn.execute(
                """
                SELECT visitor_name, host_name, visit_date, COALESCE(c.name, '') AS car_park
                FROM visitor_bookings v
                LEFT JOIN car_parks c ON c.id = v.car_park_id
                WHERE UPPER(v.vehicle_reg) = UPPER(?)
                  AND visit_date = ?
                  AND v.status IN ('Booked', 'Approved')
                ORDER BY v.id DESC LIMIT 1
                """,
                (vehicle_reg, check_date),
            ).fetchone()

            reservation = conn.execute(
                """
                SELECT reserved_for, reservation_type, contact_name, start_date, end_date,
                       COALESCE(c.name, '') AS car_park
                FROM reservations r
                LEFT JOIN car_parks c ON c.id = r.car_park_id
                WHERE UPPER(COALESCE(r.vehicle_reg,'')) = UPPER(?)
                  AND r.status = 'Active'
                  AND r.start_date <= ?
                  AND r.end_date >= ?
                ORDER BY r.id DESC LIMIT 1
                """,
                (vehicle_reg, check_date, check_date),
            ).fetchone()

            penalties = conn.execute(
                """
                SELECT id, reason, location, issued_at
                FROM penalties
                WHERE UPPER(vehicle_reg) = UPPER(?)
                ORDER BY id DESC LIMIT 5
                """,
                (vehicle_reg,),
            ).fetchall()

            return {
                "permit": permit,
                "temporary_permit": temp_permit,
                "visitor": visitor,
                "reservation": reservation,
                "penalties": penalties,
            }


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def ensure_date(value, label):
    if not value:
        return ""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError as exc:
        raise ValueError(f"{label} must be in YYYY-MM-DD format.") from exc


def parse_car_park_id(value):
    if not value:
        return None
    try:
        return int(str(value).split(" - ", 1)[0])
    except (TypeError, ValueError) as exc:
        raise ValueError("Please choose a valid car park.") from exc


def normalise_reg(reg):
    return " ".join(reg.upper().split())


class CarParkMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CCCU Car Park Monitor")
        self.geometry("1480x900")
        self.minsize(1200, 760)

        self.db = DatabaseManager(DB_PATH)
        self.car_park_choices = self.db.car_park_options()

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.build_header()
        self.build_notebook()
        self.refresh_all()

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
            text="Tkinter desktop prototype for permits, visitors, reservations, patrol checks and penalty logging.",
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.permits_tab = ttk.Frame(self.notebook, padding=12)
        self.visitors_tab = ttk.Frame(self.notebook, padding=12)
        self.reservations_tab = ttk.Frame(self.notebook, padding=12)
        self.temp_permits_tab = ttk.Frame(self.notebook, padding=12)
        self.checker_tab = ttk.Frame(self.notebook, padding=12)
        self.penalties_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.permits_tab, text="Permit Applications")
        self.notebook.add(self.visitors_tab, text="Visitor Bookings")
        self.notebook.add(self.reservations_tab, text="Reservations")
        self.notebook.add(self.temp_permits_tab, text="Temporary Permits")
        self.notebook.add(self.checker_tab, text="Permit Check")
        self.notebook.add(self.penalties_tab, text="Penalty Notices")

        self.build_dashboard_tab()
        self.build_permits_tab()
        self.build_visitors_tab()
        self.build_reservations_tab()
        self.build_temp_permits_tab()
        self.build_checker_tab()
        self.build_penalties_tab()

    def build_dashboard_tab(self):
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)

        self.kpi_frame = ttk.Frame(self.dashboard_tab)
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for idx in range(4):
            self.kpi_frame.columnconfigure(idx, weight=1)

        self.kpi_labels = {}
        kpi_titles = [
            ("car_parks", "Car parks"),
            ("total_spaces", "Canterbury total spaces"),
            ("pending_permits", "Pending permits"),
            ("approved_permits", "Approved permits"),
            ("today_visitors", "Today's visitors"),
            ("active_reservations", "Active reservations"),
            ("active_temporary_permits", "Active temporary permits"),
            ("penalties", "Penalty notices"),
        ]
        for idx, (key, title) in enumerate(kpi_titles):
            card = ttk.LabelFrame(self.kpi_frame, text=title, padding=12)
            card.grid(row=idx // 4, column=idx % 4, sticky="nsew", padx=6, pady=6)
            label = ttk.Label(card, text="0", font=("Segoe UI", 18, "bold"))
            label.pack(anchor="center", pady=8)
            self.kpi_labels[key] = label

        lower = ttk.Panedwindow(self.dashboard_tab, orient=tk.HORIZONTAL)
        lower.grid(row=1, column=0, sticky="nsew")
        lower.columnconfigure(0, weight=1)

        carparks_frame = ttk.LabelFrame(lower, text="Car park overview", padding=8)
        policy_frame = ttk.LabelFrame(lower, text="Policy reminders", padding=10)
        lower.add(carparks_frame, weight=3)
        lower.add(policy_frame, weight=2)

        carparks_frame.columnconfigure(0, weight=1)
        carparks_frame.rowconfigure(0, weight=1)

        columns = ("Campus", "Name", "Standard", "Visitor", "Electric", "Disabled", "Total")
        self.carparks_tree = ttk.Treeview(carparks_frame, columns=columns, show="headings", height=16)
        for col in columns:
            self.carparks_tree.heading(col, text=col)
            self.carparks_tree.column(col, width=120, anchor="center")
        self.carparks_tree.column("Name", width=260, anchor="w")
        self.carparks_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(carparks_frame, orient="vertical", command=self.carparks_tree.yview)
        self.carparks_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        policy_text = (
            "• Staff, students and visitors all use the system.\n\n"
            "• Permit applications are reviewed manually, not auto-approved.\n\n"
            "• Visitor spaces and temporary/event reservations need tracking so patrols can confirm who is allowed to park.\n\n"
            "• Penalty notices can be logged locally and marked as sent to the external provider.\n\n"
            "• Dates are entered as YYYY-MM-DD."
        )
        ttk.Label(policy_frame, text=policy_text, justify="left", wraplength=360).pack(fill="both", expand=True)

    def build_permits_tab(self):
        self.permits_tab.columnconfigure(1, weight=1)
        self.permits_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.permits_tab, text="New permit application", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(self.permits_tab, text="Applications", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.permit_vars = {
            "applicant_type": tk.StringVar(value="Staff"),
            "full_name": tk.StringVar(),
            "university_id": tk.StringVar(),
            "email": tk.StringVar(),
            "vehicle_reg": tk.StringVar(),
            "reason": tk.StringVar(),
            "accessibility_needs": tk.StringVar(),
            "distance_km": tk.StringVar(),
            "desired_car_park": tk.StringVar(),
            "valid_from": tk.StringVar(),
            "valid_to": tk.StringVar(),
            "reviewer_notes": tk.StringVar(),
        }

        self.build_form_field(form, "Applicant type", 0, widget="combo", variable=self.permit_vars["applicant_type"], values=["Staff", "Student"])
        self.build_form_field(form, "Full name", 1, variable=self.permit_vars["full_name"])
        self.build_form_field(form, "University ID", 2, variable=self.permit_vars["university_id"])
        self.build_form_field(form, "Email", 3, variable=self.permit_vars["email"])
        self.build_form_field(form, "Vehicle reg", 4, variable=self.permit_vars["vehicle_reg"])
        self.build_form_field(form, "Reason / justification", 5, variable=self.permit_vars["reason"])
        self.build_form_field(form, "Accessibility needs", 6, variable=self.permit_vars["accessibility_needs"])
        self.build_form_field(form, "Distance from campus (km)", 7, variable=self.permit_vars["distance_km"])
        self.build_form_field(form, "Desired car park", 8, widget="combo", variable=self.permit_vars["desired_car_park"], values=self.car_park_choices)
        self.build_form_field(form, "Valid from", 9, variable=self.permit_vars["valid_from"])
        self.build_form_field(form, "Valid to", 10, variable=self.permit_vars["valid_to"])

        ttk.Button(form, text="Save application", command=self.save_permit_application).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.permit_vars, keep={"applicant_type": "Staff"})).grid(row=12, column=0, columnspan=2, sticky="ew")

        permit_columns = ("ID", "Type", "Name", "Vehicle reg", "Email", "Car park", "Valid from", "Valid to", "Status", "Created")
        self.permits_tree = ttk.Treeview(table_frame, columns=permit_columns, show="headings", height=20)
        for col in permit_columns:
            self.permits_tree.heading(col, text=col)
            self.permits_tree.column(col, width=110, anchor="center")
        self.permits_tree.column("Name", width=160, anchor="w")
        self.permits_tree.column("Email", width=190, anchor="w")
        self.permits_tree.column("Car park", width=210, anchor="w")
        self.permits_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.permits_tree.yview)
        self.permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        review = ttk.Frame(table_frame)
        review.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        review.columnconfigure(1, weight=1)

        ttk.Label(review, text="Selected application status").grid(row=0, column=0, sticky="w")
        self.permit_status_var = tk.StringVar(value="Approved")
        ttk.Combobox(review, textvariable=self.permit_status_var, values=["Pending", "Approved", "Declined"], state="readonly", width=14).grid(row=0, column=1, sticky="w", padx=(8, 12))
        self.permit_review_notes = tk.StringVar()
        ttk.Entry(review, textvariable=self.permit_review_notes).grid(row=0, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(review, text="Update selected", command=self.update_selected_permit_status).grid(row=0, column=3, sticky="e")
        ttk.Button(review, text="Refresh", command=self.refresh_permits).grid(row=0, column=4, padx=(8, 0), sticky="e")

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

        self.build_form_field(form, "Visitor name", 0, variable=self.visitor_vars["visitor_name"])
        self.build_form_field(form, "Host name", 1, variable=self.visitor_vars["host_name"])
        self.build_form_field(form, "Host department", 2, variable=self.visitor_vars["host_department"])
        self.build_form_field(form, "Email", 3, variable=self.visitor_vars["email"])
        self.build_form_field(form, "Vehicle reg", 4, variable=self.visitor_vars["vehicle_reg"])
        self.build_form_field(form, "Visit date", 5, variable=self.visitor_vars["visit_date"])
        self.build_form_field(form, "Car park", 6, widget="combo", variable=self.visitor_vars["car_park"], values=self.car_park_choices)
        self.build_form_field(form, "Spaces required", 7, variable=self.visitor_vars["space_required"])
        self.build_form_field(form, "Notes", 8, variable=self.visitor_vars["notes"])

        ttk.Button(form, text="Save booking", command=self.save_visitor_booking).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.visitor_vars, keep={"visit_date": today_str(), "space_required": "1"})).grid(row=10, column=0, columnspan=2, sticky="ew")

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

    def build_reservations_tab(self):
        self.reservations_tab.columnconfigure(1, weight=1)
        self.reservations_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.reservations_tab, text="New reservation", padding=12)
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
            "notes": tk.StringVar(),
        }

        self.build_form_field(form, "Reserved for", 0, variable=self.reservation_vars["reserved_for"])
        self.build_form_field(form, "Reservation type", 1, widget="combo", variable=self.reservation_vars["reservation_type"], values=["Event", "Contractor", "Guest", "VIP", "Other"])
        self.build_form_field(form, "Contact name", 2, variable=self.reservation_vars["contact_name"])
        self.build_form_field(form, "Vehicle reg", 3, variable=self.reservation_vars["vehicle_reg"])
        self.build_form_field(form, "Car park", 4, widget="combo", variable=self.reservation_vars["car_park"], values=self.car_park_choices)
        self.build_form_field(form, "Bay count", 5, variable=self.reservation_vars["bay_count"])
        self.build_form_field(form, "Start date", 6, variable=self.reservation_vars["start_date"])
        self.build_form_field(form, "End date", 7, variable=self.reservation_vars["end_date"])
        self.build_form_field(form, "Notes", 8, variable=self.reservation_vars["notes"])

        ttk.Button(form, text="Save reservation", command=self.save_reservation).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.reservation_vars, keep={"reservation_type": "Event", "bay_count": "1", "start_date": today_str(), "end_date": today_str()})).grid(row=10, column=0, columnspan=2, sticky="ew")

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

    def build_temp_permits_tab(self):
        self.temp_permits_tab.columnconfigure(1, weight=1)
        self.temp_permits_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(self.temp_permits_tab, text="New temporary permit", padding=12)
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
            "notes": tk.StringVar(),
        }

        self.build_form_field(form, "Permit holder", 0, variable=self.temp_vars["permit_holder"])
        self.build_form_field(form, "Vehicle reg", 1, variable=self.temp_vars["vehicle_reg"])
        self.build_form_field(form, "Permit type", 2, widget="combo", variable=self.temp_vars["permit_type"], values=["Temporary", "Day Permit", "Contractor", "Accessible", "Replacement Vehicle"])
        self.build_form_field(form, "Start date", 3, variable=self.temp_vars["start_date"])
        self.build_form_field(form, "End date", 4, variable=self.temp_vars["end_date"])
        self.build_form_field(form, "Notes", 5, variable=self.temp_vars["notes"])

        ttk.Button(form, text="Save temporary permit", command=self.save_temporary_permit).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(form, text="Clear form", command=lambda: self.clear_vars(self.temp_vars, keep={"permit_type": "Temporary", "start_date": today_str(), "end_date": today_str()})).grid(row=7, column=0, columnspan=2, sticky="ew")

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
        self.build_form_field(form, "Reason", 1, widget="combo", variable=self.penalty_vars["reason"], values=["No valid permit", "Parked in wrong bay", "Overstayed", "Unauthorised visitor parking", "Other"])
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

    def build_form_field(self, parent, label, row, variable, widget="entry", values=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        if widget == "combo":
            control = ttk.Combobox(parent, textvariable=variable, values=values or [], state="readonly", width=32)
        else:
            control = ttk.Entry(parent, textvariable=variable, width=35)
        control.grid(row=row, column=1, sticky="ew", pady=4)
        parent.columnconfigure(1, weight=1)
        return control

    def clear_vars(self, variables, keep=None):
        keep = keep or {}
        for key, var in variables.items():
            var.set(keep.get(key, ""))

    def refresh_all(self):
        self.car_park_choices = self.db.car_park_options()
        self.refresh_dashboard()
        self.refresh_permits()
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
                values=(
                    row["campus"],
                    row["name"],
                    row["standard_bays"],
                    row["visitor_bays"],
                    row["electric_charging"],
                    row["disabled_bays"],
                    row["total_bays"],
                ),
            )

    def refresh_permits(self):
        self.replace_tree_data(self.permits_tree, self.db.list_permit_applications())

    def refresh_visitors(self):
        self.replace_tree_data(self.visitors_tree, self.db.list_visitor_bookings())

    def refresh_reservations(self):
        self.replace_tree_data(self.reservations_tree, self.db.list_reservations())

    def refresh_temp_permits(self):
        self.replace_tree_data(self.temp_tree, self.db.list_temporary_permits())

    def refresh_penalties(self):
        self.replace_tree_data(self.penalties_tree, self.db.list_penalties())

    def replace_tree_data(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=tuple(row))

    def save_permit_application(self):
        try:
            distance = self.permit_vars["distance_km"].get().strip()
            data = {
                "applicant_type": self.permit_vars["applicant_type"].get().strip(),
                "full_name": self.require(self.permit_vars["full_name"].get(), "Full name"),
                "university_id": self.permit_vars["university_id"].get().strip(),
                "email": self.require(self.permit_vars["email"].get(), "Email"),
                "vehicle_reg": normalise_reg(self.require(self.permit_vars["vehicle_reg"].get(), "Vehicle reg")),
                "reason": self.permit_vars["reason"].get().strip(),
                "accessibility_needs": self.permit_vars["accessibility_needs"].get().strip(),
                "distance_km": float(distance) if distance else None,
                "desired_car_park_id": parse_car_park_id(self.permit_vars["desired_car_park"].get()),
                "valid_from": ensure_date(self.permit_vars["valid_from"].get().strip(), "Valid from"),
                "valid_to": ensure_date(self.permit_vars["valid_to"].get().strip(), "Valid to"),
            }
            self.db.add_permit_application(data)
            self.refresh_all()
            self.clear_vars(self.permit_vars, keep={"applicant_type": "Staff"})
            messagebox.showinfo("Saved", "Permit application saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def update_selected_permit_status(self):
        selected = self.permits_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a permit application first.")
            return
        permit_id = self.permits_tree.item(selected[0], "values")[0]
        self.db.update_permit_status(permit_id, self.permit_status_var.get(), self.permit_review_notes.get().strip())
        self.refresh_all()
        messagebox.showinfo("Updated", "Permit status updated.")

    def save_visitor_booking(self):
        try:
            data = {
                "visitor_name": self.require(self.visitor_vars["visitor_name"].get(), "Visitor name"),
                "host_name": self.require(self.visitor_vars["host_name"].get(), "Host name"),
                "host_department": self.visitor_vars["host_department"].get().strip(),
                "email": self.require(self.visitor_vars["email"].get(), "Email"),
                "vehicle_reg": normalise_reg(self.require(self.visitor_vars["vehicle_reg"].get(), "Vehicle reg")),
                "visit_date": ensure_date(self.visitor_vars["visit_date"].get().strip(), "Visit date"),
                "car_park_id": parse_car_park_id(self.visitor_vars["car_park"].get()),
                "space_required": int(self.visitor_vars["space_required"].get().strip() or "1"),
                "notes": self.visitor_vars["notes"].get().strip(),
            }
            self.db.add_visitor_booking(data)
            self.refresh_all()
            self.clear_vars(self.visitor_vars, keep={"visit_date": today_str(), "space_required": "1"})
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
                "start_date": ensure_date(self.reservation_vars["start_date"].get().strip(), "Start date"),
                "end_date": ensure_date(self.reservation_vars["end_date"].get().strip(), "End date"),
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
                "start_date": ensure_date(self.temp_vars["start_date"].get().strip(), "Start date"),
                "end_date": ensure_date(self.temp_vars["end_date"].get().strip(), "End date"),
                "notes": self.temp_vars["notes"].get().strip(),
            }
            self.db.add_temporary_permit(data)
            self.refresh_all()
            self.clear_vars(self.temp_vars, keep={"permit_type": "Temporary", "start_date": today_str(), "end_date": today_str()})
            messagebox.showinfo("Saved", "Temporary permit saved.")
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

    def check_vehicle(self):
        try:
            reg = normalise_reg(self.require(self.check_reg_var.get(), "Vehicle reg"))
            check_date = ensure_date(self.check_date_var.get().strip(), "Check date")
            result = self.db.check_vehicle(reg, check_date)

            lines = [f"Vehicle check for {reg}", f"Date: {check_date}", "-" * 60]

            if result["permit"]:
                permit = result["permit"]
                lines.extend([
                    "Approved permit found",
                    f"Holder: {permit['full_name']} ({permit['applicant_type']})",
                    f"Valid: {permit['valid_from'] or 'open'} to {permit['valid_to'] or 'open'}",
                    "",
                ])
            else:
                lines.extend(["No approved standard permit found.", ""])

            if result["temporary_permit"]:
                temp = result["temporary_permit"]
                lines.extend([
                    "Temporary permit found",
                    f"Holder: {temp['permit_holder']}",
                    f"Type: {temp['permit_type']}",
                    f"Valid: {temp['start_date']} to {temp['end_date']}",
                    "",
                ])

            if result["visitor"]:
                visitor = result["visitor"]
                lines.extend([
                    "Visitor booking found",
                    f"Visitor: {visitor['visitor_name']}",
                    f"Host: {visitor['host_name']}",
                    f"Car park: {visitor['car_park']}",
                    "",
                ])

            if result["reservation"]:
                reservation = result["reservation"]
                lines.extend([
                    "Reservation found",
                    f"Reserved for: {reservation['reserved_for']}",
                    f"Type: {reservation['reservation_type']}",
                    f"Contact: {reservation['contact_name']}",
                    f"Car park: {reservation['car_park']}",
                    f"Dates: {reservation['start_date']} to {reservation['end_date']}",
                    "",
                ])

            if not any([result["permit"], result["temporary_permit"], result["visitor"], result["reservation"]]):
                lines.extend([
                    "No current permit, visitor booking, temporary permit or reservation found.",
                    "This vehicle may need further checking by patrol staff.",
                    "",
                ])

            lines.append("Recent penalty history")
            if result["penalties"]:
                for penalty in result["penalties"]:
                    lines.append(
                        f"• #{penalty['id']} | {penalty['reason']} | {penalty['location']} | {penalty['issued_at']}"
                    )
            else:
                lines.append("• No previous penalty notices recorded.")

            self.check_result.delete("1.0", tk.END)
            self.check_result.insert("1.0", "\n".join(lines))
        except Exception as exc:
            messagebox.showerror("Could not check vehicle", str(exc))

    def require(self, value, label):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{label} is required.")
        return cleaned


if __name__ == "__main__":
    app = CarParkMonitorApp()
    app.mainloop()
