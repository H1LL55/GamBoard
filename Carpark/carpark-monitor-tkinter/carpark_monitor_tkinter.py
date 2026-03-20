import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
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
    {"campus": "Tunbridge Wells", "name": "Salomons / Meadow Road (limited parking)", "standard_bays": 0, "visitor_bays": 0, "short_stay_bays": 0, "electric_charging": 2, "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0, "department_bays": 0, "total_bays": 2},
]

INELIGIBLE_EMPLOYMENT = {"Sessional", "Contractor", "Associate", "Self-employed"}
PERMIT_APP_STATUSES = [
    "Pending HoD Review",
    "Awaiting SMT Approval",
    "Approved",
    "Declined",
    "Appeal Received",
    "Appeal Upheld",
    "Appeal Declined",
]
ISSUED_PERMIT_STATUSES = [
    "Ready for Collection",
    "Collected",
    "Active",
    "Cancelled",
    "Returned",
    "Lost/Replacement Ordered",
]
PERMIT_KIND_OPTIONS = [
    "Standard",
    "Friday Only",
    "Medway Only",
    "Tunbridge Wells Only",
    "Accessible",
    "Business User",
]
TEMP_PERMIT_OPTIONS = [
    "Temporary",
    "Day Permit",
    "Contractor",
    "Accessible",
    "Replacement Vehicle",
    "Friday Only",
    "Daily EV Charging Permit",
    "Visitor Day Permit",
]
COLLECTION_LOCATIONS = [
    "Old Sessions House reception",
    "Medway reception",
    "Tunbridge Wells reception",
]


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def default_expiry_str():
    return "2026-08-31"


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def ensure_date(value, label, allow_blank=True):
    value = (value or "").strip()
    if not value:
        if allow_blank:
            return ""
        raise ValueError(f"{label} is required.")
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
    return " ".join((reg or "").upper().split())


def as_yes_no(flag: bool) -> str:
    return "Yes" if flag else "No"


def today_plus_days(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def default_collection_for_campus(campus: str) -> str:
    mapping = {
        "Canterbury": "Old Sessions House reception",
        "Medway": "Medway reception",
        "Tunbridge Wells": "Tunbridge Wells reception",
    }
    return mapping.get(campus or "", "Old Sessions House reception")


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.initialise()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
                    status TEXT NOT NULL DEFAULT 'Pending HoD Review',
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

                CREATE TABLE IF NOT EXISTS issued_permits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER,
                    permit_number TEXT NOT NULL UNIQUE,
                    permit_kind TEXT NOT NULL,
                    campus_scope TEXT NOT NULL,
                    holder_name TEXT NOT NULL,
                    vehicle_reg_primary TEXT NOT NULL,
                    vehicle_reg_secondary TEXT,
                    issue_reason TEXT,
                    issued_date TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    collection_location TEXT,
                    status TEXT NOT NULL DEFAULT 'Ready for Collection',
                    replacement_fee_due REAL NOT NULL DEFAULT 0,
                    notes TEXT,
                    return_received INTEGER NOT NULL DEFAULT 0,
                    cancelled_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (application_id) REFERENCES permit_applications(id)
                );
                """
            )
            self.migrate(conn)
            self.seed_car_parks(conn)

    def table_columns(self, conn, table_name):
        return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}

    def add_column_if_missing(self, conn, table, column_def):
        column_name = column_def.split()[0]
        if column_name not in self.table_columns(conn, table):
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")

    def migrate(self, conn):
        for col in [
            "campus TEXT DEFAULT 'Canterbury'",
            "department TEXT",
            "contact_number TEXT",
            "home_postcode TEXT",
            "employment_type TEXT DEFAULT 'Salaried'",
            "payroll_number TEXT",
            "secondary_vehicle_reg TEXT",
            "blue_badge INTEGER NOT NULL DEFAULT 0",
            "mobility_need INTEGER NOT NULL DEFAULT 0",
            "registered_carer INTEGER NOT NULL DEFAULT 0",
            "child_under_11 INTEGER NOT NULL DEFAULT 0",
            "essential_business_user INTEGER NOT NULL DEFAULT 0",
            "business_travel_trips INTEGER NOT NULL DEFAULT 0",
            "business_insurance INTEGER NOT NULL DEFAULT 0",
            "friday_only_requested INTEGER NOT NULL DEFAULT 0",
            "planned_days TEXT",
            "evidence_summary TEXT",
            "head_recommended_by TEXT",
            "head_recommendation TEXT DEFAULT 'Pending'",
            "head_recommendation_date TEXT",
            "smt_decided_by TEXT",
            "smt_decision TEXT DEFAULT 'Pending'",
            "smt_decision_date TEXT",
            "appeal_status TEXT DEFAULT 'No Appeal'",
            "permit_scope TEXT",
            "collection_location TEXT",
        ]:
            self.add_column_if_missing(conn, "permit_applications", col)

        for col in ["booked_in_advance INTEGER NOT NULL DEFAULT 1", "permit_issued_in_advance INTEGER NOT NULL DEFAULT 1"]:
            self.add_column_if_missing(conn, "visitor_bookings", col)
        for col in ["approved_by TEXT"]:
            self.add_column_if_missing(conn, "reservations", col)
        for col in ["approved_by TEXT", "reason_recorded TEXT"]:
            self.add_column_if_missing(conn, "temporary_permits", col)
        for col in ["amount_full REAL NOT NULL DEFAULT 70", "amount_discounted REAL NOT NULL DEFAULT 35", "discount_deadline TEXT"]:
            self.add_column_if_missing(conn, "penalties", col)

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
                    park["campus"], park["name"], park["standard_bays"], park["visitor_bays"],
                    park["short_stay_bays"], park["electric_charging"], park["disabled_bays"],
                    park["contractor_bays"], park["motorcycle_bays"], park["department_bays"], park["total_bays"],
                ),
            )

    def fetch_car_parks(self):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM car_parks ORDER BY campus, name").fetchall()

    def car_park_options(self):
        return [f"{row['id']} - {row['campus']} - {row['name']}" for row in self.fetch_car_parks()]

    def add_permit_application(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO permit_applications (
                    applicant_type, campus, full_name, university_id, payroll_number, email, department,
                    contact_number, home_postcode, employment_type, vehicle_reg, secondary_vehicle_reg,
                    reason, accessibility_needs, distance_km, desired_car_park_id, valid_from, valid_to,
                    status, reviewer_notes, created_at, blue_badge, mobility_need, registered_carer,
                    child_under_11, essential_business_user, business_travel_trips, business_insurance,
                    friday_only_requested, planned_days, evidence_summary, permit_scope, collection_location,
                    head_recommendation, smt_decision, appeal_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["applicant_type"], data["campus"], data["full_name"], data["university_id"],
                    data["payroll_number"], data["email"], data["department"], data["contact_number"],
                    data["home_postcode"], data["employment_type"], data["vehicle_reg"],
                    data["secondary_vehicle_reg"], data["reason"], data["accessibility_needs"], data["distance_km"],
                    data["desired_car_park_id"], data["valid_from"], data["valid_to"], "Pending HoD Review", "",
                    now_str(), int(data["blue_badge"]), int(data["mobility_need"]), int(data["registered_carer"]),
                    int(data["child_under_11"]), int(data["essential_business_user"]), data["business_travel_trips"],
                    int(data["business_insurance"]), int(data["friday_only_requested"]), data["planned_days"],
                    data["evidence_summary"], data["permit_scope"], data["collection_location"], "Pending", "Pending", "No Appeal",
                ),
            )

    def list_permit_applications(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT p.id, p.applicant_type, p.campus, p.full_name, p.vehicle_reg,
                       COALESCE(p.secondary_vehicle_reg, '') AS secondary_vehicle_reg,
                       p.employment_type, p.email,
                       COALESCE(c.name, '') AS car_park, p.status, p.created_at
                FROM permit_applications p
                LEFT JOIN car_parks c ON c.id = p.desired_car_park_id
                ORDER BY p.id DESC
                """
            ).fetchall()

    def get_permit_application(self, permit_id):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT p.*, COALESCE(c.name, '') AS car_park_name
                FROM permit_applications p
                LEFT JOIN car_parks c ON c.id = p.desired_car_park_id
                WHERE p.id = ?
                """,
                (permit_id,),
            ).fetchone()

    def update_permit_status(self, permit_id, status, reviewer_name, notes):
        with self.connect() as conn:
            fields = {"status": status, "reviewer_notes": notes}
            if status == "Awaiting SMT Approval":
                fields.update({"head_recommendation": "Supported", "head_recommended_by": reviewer_name, "head_recommendation_date": today_str()})
            elif status == "Approved":
                fields.update({"smt_decision": "Approved", "smt_decided_by": reviewer_name, "smt_decision_date": today_str()})
            elif status == "Declined":
                fields.update({"smt_decision": "Declined", "smt_decided_by": reviewer_name, "smt_decision_date": today_str()})
            elif status.startswith("Appeal"):
                fields["appeal_status"] = status
            assignments = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [permit_id]
            conn.execute(f"UPDATE permit_applications SET {assignments} WHERE id = ?", values)

    def next_permit_number(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM issued_permits").fetchone()[0] + 1
        return f"CCCU-P-{date.today().year}-{count:04d}"

    def issue_permit_from_application(self, application_id, permit_kind, campus_scope, expiry_date, collection_location, notes):
        with self.connect() as conn:
            app = conn.execute("SELECT * FROM permit_applications WHERE id = ?", (application_id,)).fetchone()
            if not app:
                raise ValueError("Permit application not found.")
            if app["status"] != "Approved":
                raise ValueError("Only approved applications can be issued as permits.")
            existing = conn.execute(
                "SELECT id FROM issued_permits WHERE application_id = ? AND status NOT IN ('Cancelled', 'Returned')",
                (application_id,),
            ).fetchone()
            if existing:
                raise ValueError("A live issued permit already exists for this application.")
            conn.execute(
                """
                INSERT INTO issued_permits (
                    application_id, permit_number, permit_kind, campus_scope, holder_name,
                    vehicle_reg_primary, vehicle_reg_secondary, issue_reason, issued_date,
                    expiry_date, collection_location, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id, self.next_permit_number(conn), permit_kind, campus_scope or app["campus"], app["full_name"],
                    app["vehicle_reg"], app["secondary_vehicle_reg"], app["reason"] or "Issued from approved application",
                    today_str(), expiry_date, collection_location or app["collection_location"] or default_collection_for_campus(app["campus"]),
                    "Ready for Collection", notes, now_str(),
                ),
            )

    def list_issued_permits(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, permit_number, holder_name, permit_kind, campus_scope,
                       vehicle_reg_primary, COALESCE(vehicle_reg_secondary, '') AS vehicle_reg_secondary,
                       issued_date, expiry_date, status
                FROM issued_permits
                ORDER BY id DESC
                """
            ).fetchall()

    def get_issued_permit(self, permit_id):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM issued_permits WHERE id = ?", (permit_id,)).fetchone()

    def update_issued_permit(self, permit_id, status, notes, replacement_fee_due=0):
        with self.connect() as conn:
            fields = {"status": status, "notes": notes, "replacement_fee_due": replacement_fee_due}
            if status in {"Cancelled", "Returned"}:
                fields["cancelled_at"] = now_str()
            if status == "Returned":
                fields["return_received"] = 1
            assignments = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [permit_id]
            conn.execute(f"UPDATE issued_permits SET {assignments} WHERE id = ?", values)

    def update_issued_permit_regs(self, permit_id, reg1, reg2):
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE issued_permits
                SET vehicle_reg_primary = ?, vehicle_reg_secondary = ?, notes = COALESCE(notes, '') || ?
                WHERE id = ?
                """,
                (normalise_reg(reg1), normalise_reg(reg2) if reg2 else "", f"\n[{now_str()}] Vehicle details updated.", permit_id),
            )

    def add_visitor_booking(self, data):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO visitor_bookings (
                    visitor_name, host_name, host_department, email, vehicle_reg, visit_date,
                    car_park_id, space_required, status, notes, created_at, booked_in_advance,
                    permit_issued_in_advance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["visitor_name"], data["host_name"], data["host_department"], data["email"], data["vehicle_reg"],
                    data["visit_date"], data["car_park_id"], data["space_required"], "Booked", data["notes"], now_str(),
                    int(data["booked_in_advance"]), int(data["permit_issued_in_advance"]),
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
                    bay_count, start_date, end_date, status, notes, created_at, approved_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["reserved_for"], data["reservation_type"], data["contact_name"], data["vehicle_reg"],
                    data["car_park_id"], data["bay_count"], data["start_date"], data["end_date"], "Active",
                    data["notes"], now_str(), data["approved_by"],
                ),
            )

    def list_reservations(self):
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT r.id, r.reserved_for, r.reservation_type, r.contact_name,
                       COALESCE(r.vehicle_reg, '') AS vehicle_reg, r.start_date, r.end_date,
                       r.bay_count, COALESCE(c.name, '') AS car_park, r.status
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
                    status, notes, created_at, approved_by, reason_recorded
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["permit_holder"], data["vehicle_reg"], data["permit_type"], data["start_date"], data["end_date"],
                    "Active", data["notes"], now_str(), data["approved_by"], data["reason_recorded"],
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
                    appeal_status, notes, issued_at, amount_full, amount_discounted, discount_deadline
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["vehicle_reg"], data["reason"], data["location"], data["issued_by"], data["external_status"],
                    data["appeal_status"], data["notes"], now_str(), 70, 35, today_plus_days(14),
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
                "pending_permits": conn.execute("SELECT COUNT(*) FROM permit_applications WHERE status IN ('Pending HoD Review', 'Awaiting SMT Approval')").fetchone()[0],
                "approved_permits": conn.execute("SELECT COUNT(*) FROM permit_applications WHERE status='Approved'").fetchone()[0],
                "issued_permits": conn.execute("SELECT COUNT(*) FROM issued_permits WHERE status NOT IN ('Cancelled', 'Returned')").fetchone()[0],
                "friday_only": conn.execute("SELECT COUNT(*) FROM issued_permits WHERE permit_kind='Friday Only' AND status NOT IN ('Cancelled', 'Returned')").fetchone()[0],
                "today_visitors": conn.execute("SELECT COUNT(*) FROM visitor_bookings WHERE visit_date = ?", (today_str(),)).fetchone()[0],
                "active_reservations": conn.execute("SELECT COUNT(*) FROM reservations WHERE status='Active' AND start_date <= ? AND end_date >= ?", (today_str(), today_str())).fetchone()[0],
                "active_temporary_permits": conn.execute("SELECT COUNT(*) FROM temporary_permits WHERE status='Active' AND start_date <= ? AND end_date >= ?", (today_str(), today_str())).fetchone()[0],
                "penalties": conn.execute("SELECT COUNT(*) FROM penalties").fetchone()[0],
            }

    def check_vehicle(self, vehicle_reg, check_date):
        with self.connect() as conn:
            issued = conn.execute(
                """
                SELECT *
                FROM issued_permits
                WHERE (UPPER(vehicle_reg_primary) = UPPER(?) OR UPPER(COALESCE(vehicle_reg_secondary, '')) = UPPER(?))
                  AND status IN ('Collected', 'Active')
                  AND issued_date <= ?
                  AND expiry_date >= ?
                ORDER BY id DESC
                """,
                (vehicle_reg, vehicle_reg, check_date, check_date),
            ).fetchall()
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
            return {"issued_permits": issued, "temporary_permit": temp_permit, "visitor": visitor, "reservation": reservation, "penalties": penalties}


class CarParkMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CCCU Car Park Monitor")
        self.geometry("1680x980")
        self.minsize(1320, 820)
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
        ttk.Label(header, text="CCCU Car Park Monitor", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Desktop prototype aligned more closely to the policy/forms: eligibility criteria, HoD/SMT review, issued permits, visitors, reservations, patrol checks and penalty logging.",
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

    def build_dashboard_tab(self):
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)
        self.kpi_frame = ttk.Frame(self.dashboard_tab)
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for idx in range(5):
            self.kpi_frame.columnconfigure(idx, weight=1)
        self.kpi_labels = {}
        kpi_titles = [
            ("car_parks", "Car parks"), ("total_spaces", "Canterbury total spaces"), ("pending_permits", "Pending permit reviews"),
            ("approved_permits", "Approved applications"), ("issued_permits", "Issued permits"), ("friday_only", "Friday-only permits"),
            ("today_visitors", "Today's visitors"), ("active_reservations", "Active reservations"), ("active_temporary_permits", "Active temp/day permits"), ("penalties", "Penalty notices"),
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
        policy_frame = ttk.LabelFrame(lower, text="Policy reminders included in this version", padding=10)
        lower.add(carparks_frame, weight=3)
        lower.add(policy_frame, weight=2)
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
        policy_text = (
            "• Staff permit applications now capture the main eligibility criteria from the staff form.\n\n"
            "• Applications move through HoD review and SMT approval rather than instant approval.\n\n"
            "• Up to 2 vehicle registrations can be stored for staff permits.\n\n"
            "• Friday-only permits and campus-specific permits can be issued.\n\n"
            "• Temporary/day/EV/visitor permits can be recorded locally.\n\n"
            "• Issued permits can be collected, cancelled, returned, or replaced.\n\n"
            "• Patrol checks now look at issued permits first, then temporary/day/visitor/reservation records.\n\n"
            "• PCNs default to £70, reduced to £35 if paid within 14 days."
        )
        ttk.Label(policy_frame, text=policy_text, justify="left", wraplength=430).pack(fill="both", expand=True)

    def build_permits_tab(self):
        self.permits_tab.columnconfigure(1, weight=1)
        self.permits_tab.rowconfigure(0, weight=1)
        form = ttk.LabelFrame(self.permits_tab, text="New permit application", padding=12)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        table_frame = ttk.LabelFrame(self.permits_tab, text="Applications and review", padding=8)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.permit_vars = {
            "applicant_type": tk.StringVar(value="Staff"), "campus": tk.StringVar(value="Canterbury"), "full_name": tk.StringVar(),
            "university_id": tk.StringVar(), "payroll_number": tk.StringVar(), "department": tk.StringVar(), "contact_number": tk.StringVar(),
            "email": tk.StringVar(), "employment_type": tk.StringVar(value="Salaried"), "home_postcode": tk.StringVar(),
            "vehicle_reg": tk.StringVar(), "secondary_vehicle_reg": tk.StringVar(), "reason": tk.StringVar(),
            "accessibility_needs": tk.StringVar(), "distance_km": tk.StringVar(), "desired_car_park": tk.StringVar(),
            "valid_from": tk.StringVar(value=today_str()), "valid_to": tk.StringVar(value=default_expiry_str()), "business_travel_trips": tk.StringVar(value="0"),
            "planned_days": tk.StringVar(), "evidence_summary": tk.StringVar(), "permit_scope": tk.StringVar(value="Campus default"),
            "collection_location": tk.StringVar(value="Old Sessions House reception"),
        }
        row = 0
        self.build_form_field(form, "Applicant type", row, widget="combo", variable=self.permit_vars["applicant_type"], values=["Staff", "Student"]); row += 1
        self.build_form_field(form, "Campus", row, widget="combo", variable=self.permit_vars["campus"], values=["Canterbury", "Medway", "Tunbridge Wells"]); row += 1
        self.build_form_field(form, "Full name", row, variable=self.permit_vars["full_name"]); row += 1
        self.build_form_field(form, "University / student ID", row, variable=self.permit_vars["university_id"]); row += 1
        self.build_form_field(form, "Payroll no. (staff)", row, variable=self.permit_vars["payroll_number"]); row += 1
        self.build_form_field(form, "Department", row, variable=self.permit_vars["department"]); row += 1
        self.build_form_field(form, "Contact number", row, variable=self.permit_vars["contact_number"]); row += 1
        self.build_form_field(form, "Email", row, variable=self.permit_vars["email"]); row += 1
        self.build_form_field(form, "Employment type", row, widget="combo", variable=self.permit_vars["employment_type"], values=["Salaried", "Contracted", "Temporary", "Casual", "On Secondment", "KMMS", "Sessional", "Contractor", "Associate", "Self-employed"]); row += 1
        self.build_form_field(form, "Home postcode", row, variable=self.permit_vars["home_postcode"]); row += 1
        self.build_form_field(form, "Vehicle reg 1", row, variable=self.permit_vars["vehicle_reg"]); row += 1
        self.build_form_field(form, "Vehicle reg 2", row, variable=self.permit_vars["secondary_vehicle_reg"]); row += 1
        self.build_form_field(form, "Reason / justification", row, variable=self.permit_vars["reason"]); row += 1
        self.build_form_field(form, "Accessibility / health notes", row, variable=self.permit_vars["accessibility_needs"]); row += 1
        self.build_form_field(form, "Distance from campus (km)", row, variable=self.permit_vars["distance_km"]); row += 1
        self.build_form_field(form, "Desired car park", row, widget="combo", variable=self.permit_vars["desired_car_park"], values=self.car_park_choices); row += 1
        self.build_form_field(form, "Valid from", row, variable=self.permit_vars["valid_from"]); row += 1
        self.build_form_field(form, "Valid to", row, variable=self.permit_vars["valid_to"]); row += 1
        criteria_frame = ttk.LabelFrame(form, text="Eligibility criteria", padding=8)
        criteria_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(6, 6))
        criteria_frame.columnconfigure(0, weight=1)
        criteria_frame.columnconfigure(1, weight=1)
        self.blue_badge_var = tk.BooleanVar(value=False)
        self.mobility_need_var = tk.BooleanVar(value=False)
        self.registered_carer_var = tk.BooleanVar(value=False)
        self.child_under_11_var = tk.BooleanVar(value=False)
        self.essential_business_var = tk.BooleanVar(value=False)
        self.business_insurance_var = tk.BooleanVar(value=False)
        self.friday_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(criteria_frame, text="Blue Badge holder", variable=self.blue_badge_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Mobility / health condition", variable=self.mobility_need_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Registered carer", variable=self.registered_carer_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Child aged 11 or under", variable=self.child_under_11_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Essential business user", variable=self.essential_business_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Business insurance confirmed", variable=self.business_insurance_var).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Friday-only permit requested", variable=self.friday_only_var).grid(row=3, column=0, sticky="w")
        row += 1
        self.build_form_field(form, "Business travel trips / week", row, variable=self.permit_vars["business_travel_trips"]); row += 1
        self.build_form_field(form, "Expected campus days", row, variable=self.permit_vars["planned_days"]); row += 1
        self.build_form_field(form, "Evidence / notes summary", row, variable=self.permit_vars["evidence_summary"]); row += 1
        self.build_form_field(form, "Permit scope", row, widget="combo", variable=self.permit_vars["permit_scope"], values=["Campus default", "Canterbury", "Medway only", "Tunbridge Wells only", "Friday only"]); row += 1
        self.build_form_field(form, "Collection location", row, widget="combo", variable=self.permit_vars["collection_location"], values=COLLECTION_LOCATIONS); row += 1
        ttk.Button(form, text="Save application", command=self.save_permit_application).grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 4)); row += 1
        ttk.Button(form, text="Clear form", command=self.clear_permit_form).grid(row=row, column=0, columnspan=2, sticky="ew")
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
        for idx in range(8):
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
        ttk.Button(review, text="View selected", command=self.show_selected_permit_details).grid(row=0, column=7, sticky="ew", padx=(8, 0))
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
            "visitor_name": tk.StringVar(), "host_name": tk.StringVar(), "host_department": tk.StringVar(),
            "email": tk.StringVar(), "vehicle_reg": tk.StringVar(), "visit_date": tk.StringVar(value=today_str()),
            "car_park": tk.StringVar(), "space_required": tk.StringVar(value="1"), "notes": tk.StringVar(),
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
            "reserved_for": tk.StringVar(), "reservation_type": tk.StringVar(value="Event"), "contact_name": tk.StringVar(),
            "vehicle_reg": tk.StringVar(), "car_park": tk.StringVar(), "bay_count": tk.StringVar(value="1"),
            "start_date": tk.StringVar(value=today_str()), "end_date": tk.StringVar(value=today_str()), "approved_by": tk.StringVar(), "notes": tk.StringVar(),
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
            "permit_holder": tk.StringVar(), "vehicle_reg": tk.StringVar(), "permit_type": tk.StringVar(value="Temporary"),
            "start_date": tk.StringVar(value=today_str()), "end_date": tk.StringVar(value=today_str()), "approved_by": tk.StringVar(),
            "reason_recorded": tk.StringVar(), "notes": tk.StringVar(),
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
            "vehicle_reg": tk.StringVar(), "reason": tk.StringVar(value="No valid permit"), "location": tk.StringVar(),
            "issued_by": tk.StringVar(), "external_status": tk.StringVar(value="Sent to Workflow Dynamics"), "appeal_status": tk.StringVar(value="No Appeal"), "notes": tk.StringVar(),
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

    def clear_permit_form(self):
        self.clear_vars(self.permit_vars, keep={
            "applicant_type": "Staff", "campus": "Canterbury", "employment_type": "Salaried", "valid_from": today_str(),
            "valid_to": default_expiry_str(), "business_travel_trips": "0", "permit_scope": "Campus default", "collection_location": "Old Sessions House reception",
        })
        for flag in [self.blue_badge_var, self.mobility_need_var, self.registered_carer_var, self.child_under_11_var, self.essential_business_var, self.business_insurance_var, self.friday_only_var]:
            flag.set(False)

    def refresh_all(self):
        self.car_park_choices = self.db.car_park_options()
        self.refresh_dashboard(); self.refresh_permits(); self.refresh_issued_permits(); self.refresh_visitors(); self.refresh_reservations(); self.refresh_temp_permits(); self.refresh_penalties()

    def refresh_dashboard(self):
        counts = self.db.dashboard_counts()
        for key, label in self.kpi_labels.items():
            label.config(text=str(counts.get(key, 0)))
        for item in self.carparks_tree.get_children():
            self.carparks_tree.delete(item)
        for row in self.db.fetch_car_parks():
            self.carparks_tree.insert("", "end", values=(row["campus"], row["name"], row["standard_bays"], row["visitor_bays"], row["electric_charging"], row["disabled_bays"], row["total_bays"]))

    def refresh_permits(self): self.replace_tree_data(self.permits_tree, self.db.list_permit_applications())
    def refresh_issued_permits(self): self.replace_tree_data(self.issued_permits_tree, self.db.list_issued_permits())
    def refresh_visitors(self): self.replace_tree_data(self.visitors_tree, self.db.list_visitor_bookings())
    def refresh_reservations(self): self.replace_tree_data(self.reservations_tree, self.db.list_reservations())
    def refresh_temp_permits(self): self.replace_tree_data(self.temp_tree, self.db.list_temporary_permits())
    def refresh_penalties(self): self.replace_tree_data(self.penalties_tree, self.db.list_penalties())

    def replace_tree_data(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=tuple(row))

    def require(self, value, label):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError(f"{label} is required.")
        return cleaned

    def selected_tree_id(self, tree):
        selected = tree.selection()
        return tree.item(selected[0], "values")[0] if selected else None

    def save_permit_application(self):
        try:
            campus = self.permit_vars["campus"].get().strip()
            applicant_type = self.permit_vars["applicant_type"].get().strip()
            employment_type = self.permit_vars["employment_type"].get().strip()
            blue_badge = self.blue_badge_var.get(); mobility_need = self.mobility_need_var.get(); registered_carer = self.registered_carer_var.get(); child_under_11 = self.child_under_11_var.get(); essential_business_user = self.essential_business_var.get(); business_insurance = self.business_insurance_var.get(); friday_only = self.friday_only_var.get()
            if applicant_type == "Staff" and employment_type in INELIGIBLE_EMPLOYMENT and not friday_only:
                raise ValueError("This employment type is not eligible for a standard staff permit in the supplied documents.")
            if applicant_type == "Staff" and not any([blue_badge, mobility_need, registered_carer, child_under_11, essential_business_user, friday_only]):
                raise ValueError("Staff applications should match at least one eligibility criterion, or be marked as Friday-only.")
            trips_per_week = int(self.permit_vars["business_travel_trips"].get().strip() or "0")
            if essential_business_user and (trips_per_week < 3 or not business_insurance):
                raise ValueError("Essential business users should have at least 3 business trips per week and business insurance recorded.")
            distance = self.permit_vars["distance_km"].get().strip()
            distance_km = float(distance) if distance else None
            if applicant_type == "Staff" and campus == "Canterbury" and distance_km is not None and distance_km < 4.83 and not any([blue_badge, mobility_need, essential_business_user, friday_only]):
                messagebox.showwarning("Distance warning", "This Canterbury staff application appears to be within 3 miles. It has still been saved for manual review.")
            data = {
                "applicant_type": applicant_type, "campus": campus, "full_name": self.require(self.permit_vars["full_name"].get(), "Full name"),
                "university_id": self.permit_vars["university_id"].get().strip(), "payroll_number": self.permit_vars["payroll_number"].get().strip(),
                "department": self.permit_vars["department"].get().strip(), "contact_number": self.permit_vars["contact_number"].get().strip(),
                "email": self.require(self.permit_vars["email"].get(), "Email"), "employment_type": employment_type, "home_postcode": self.permit_vars["home_postcode"].get().strip(),
                "vehicle_reg": normalise_reg(self.require(self.permit_vars["vehicle_reg"].get(), "Vehicle reg 1")), "secondary_vehicle_reg": normalise_reg(self.permit_vars["secondary_vehicle_reg"].get().strip()),
                "reason": self.permit_vars["reason"].get().strip(), "accessibility_needs": self.permit_vars["accessibility_needs"].get().strip(), "distance_km": distance_km,
                "desired_car_park_id": parse_car_park_id(self.permit_vars["desired_car_park"].get()), "valid_from": ensure_date(self.permit_vars["valid_from"].get(), "Valid from"),
                "valid_to": ensure_date(self.permit_vars["valid_to"].get(), "Valid to"), "blue_badge": blue_badge, "mobility_need": mobility_need, "registered_carer": registered_carer,
                "child_under_11": child_under_11, "essential_business_user": essential_business_user, "business_travel_trips": trips_per_week, "business_insurance": business_insurance,
                "friday_only_requested": friday_only, "planned_days": self.permit_vars["planned_days"].get().strip(), "evidence_summary": self.permit_vars["evidence_summary"].get().strip(),
                "permit_scope": self.permit_vars["permit_scope"].get().strip(), "collection_location": self.permit_vars["collection_location"].get().strip() or default_collection_for_campus(campus),
            }
            self.db.add_permit_application(data)
            self.refresh_all(); self.clear_permit_form(); messagebox.showinfo("Saved", "Permit application saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def update_selected_permit_status(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select a permit application first."); return
            reviewer = self.require(self.permit_reviewer_var.get(), "Reviewer")
            self.db.update_permit_status(permit_id, self.permit_status_var.get(), reviewer, self.permit_review_notes.get().strip())
            self.refresh_all(); messagebox.showinfo("Updated", "Permit status updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def issue_selected_permit(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an approved application first."); return
            expiry = ensure_date(self.issue_expiry_var.get(), "Issue expiry", allow_blank=False)
            self.db.issue_permit_from_application(permit_id, self.issue_permit_kind_var.get().strip(), self.issue_scope_var.get().strip(), expiry, self.issue_collection_var.get().strip(), self.permit_review_notes.get().strip())
            self.refresh_all(); messagebox.showinfo("Issued", "Permit created and marked ready for collection.")
        except Exception as exc:
            messagebox.showerror("Could not issue", str(exc))

    def show_text_window(self, title, text):
        top = tk.Toplevel(self); top.title(title); top.geometry("760x640"); top.transient(self)
        frame = ttk.Frame(top, padding=12); frame.pack(fill="both", expand=True)
        text_box = tk.Text(frame, wrap="word", font=("Consolas", 10)); text_box.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview); scroll.pack(side="right", fill="y")
        text_box.configure(yscrollcommand=scroll.set); text_box.insert("1.0", text); text_box.configure(state="disabled")

    def show_selected_permit_details(self):
        permit_id = self.selected_tree_id(self.permits_tree)
        if not permit_id:
            messagebox.showwarning("No selection", "Please select an application first."); return
        record = self.db.get_permit_application(permit_id)
        details = [
            f"Application #{record['id']}", f"Applicant: {record['full_name']} ({record['applicant_type']})", f"Campus: {record['campus']}", f"Email: {record['email']}",
            f"Department: {record['department'] or '-'}", f"Payroll / University ID: {record['payroll_number'] or record['university_id'] or '-'}", f"Contact number: {record['contact_number'] or '-'}",
            f"Employment type: {record['employment_type'] or '-'}", f"Home postcode: {record['home_postcode'] or '-'}", f"Vehicle reg 1: {record['vehicle_reg']}",
            f"Vehicle reg 2: {record['secondary_vehicle_reg'] or '-'}", f"Desired car park: {record['car_park_name'] or '-'}", f"Requested dates: {record['valid_from'] or '-'} to {record['valid_to'] or '-'}",
            "", "Eligibility flags", f"  Blue Badge: {as_yes_no(bool(record['blue_badge']))}", f"  Mobility / health condition: {as_yes_no(bool(record['mobility_need']))}",
            f"  Registered carer: {as_yes_no(bool(record['registered_carer']))}", f"  Child 11 or under: {as_yes_no(bool(record['child_under_11']))}", f"  Essential business user: {as_yes_no(bool(record['essential_business_user']))}",
            f"  Business travel trips/week: {record['business_travel_trips']}", f"  Business insurance: {as_yes_no(bool(record['business_insurance']))}", f"  Friday-only requested: {as_yes_no(bool(record['friday_only_requested']))}",
            "", f"Reason: {record['reason'] or '-'}", f"Accessibility / health notes: {record['accessibility_needs'] or '-'}", f"Evidence summary: {record['evidence_summary'] or '-'}", f"Planned days: {record['planned_days'] or '-'}",
            f"Permit scope: {record['permit_scope'] or '-'}", f"Collection location: {record['collection_location'] or '-'}", "", "Authorisation",
            f"Status: {record['status']}", f"HoD recommendation: {record['head_recommendation']} by {record['head_recommended_by'] or '-'} on {record['head_recommendation_date'] or '-'}",
            f"SMT decision: {record['smt_decision']} by {record['smt_decided_by'] or '-'} on {record['smt_decision_date'] or '-'}", f"Appeal status: {record['appeal_status']}", f"Reviewer notes: {record['reviewer_notes'] or '-'}",
        ]
        self.show_text_window(f"Permit application #{record['id']}", "\n".join(details))

    def save_visitor_booking(self):
        try:
            data = {
                "visitor_name": self.require(self.visitor_vars["visitor_name"].get(), "Visitor name"), "host_name": self.require(self.visitor_vars["host_name"].get(), "Host name"),
                "host_department": self.visitor_vars["host_department"].get().strip(), "email": self.require(self.visitor_vars["email"].get(), "Email"),
                "vehicle_reg": normalise_reg(self.require(self.visitor_vars["vehicle_reg"].get(), "Vehicle reg")), "visit_date": ensure_date(self.visitor_vars["visit_date"].get(), "Visit date", allow_blank=False),
                "car_park_id": parse_car_park_id(self.visitor_vars["car_park"].get()), "space_required": int(self.visitor_vars["space_required"].get().strip() or "1"), "notes": self.visitor_vars["notes"].get().strip(),
                "booked_in_advance": self.visitor_booked_advance_var.get(), "permit_issued_in_advance": self.visitor_permit_advance_var.get(),
            }
            self.db.add_visitor_booking(data); self.refresh_all(); self.clear_vars(self.visitor_vars, keep={"visit_date": today_str(), "space_required": "1"}); self.visitor_booked_advance_var.set(True); self.visitor_permit_advance_var.set(True); messagebox.showinfo("Saved", "Visitor booking saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_reservation(self):
        try:
            data = {
                "reserved_for": self.require(self.reservation_vars["reserved_for"].get(), "Reserved for"), "reservation_type": self.reservation_vars["reservation_type"].get().strip(),
                "contact_name": self.require(self.reservation_vars["contact_name"].get(), "Contact name"), "vehicle_reg": normalise_reg(self.reservation_vars["vehicle_reg"].get().strip()) if self.reservation_vars["vehicle_reg"].get().strip() else "",
                "car_park_id": parse_car_park_id(self.reservation_vars["car_park"].get()), "bay_count": int(self.reservation_vars["bay_count"].get().strip() or "1"),
                "start_date": ensure_date(self.reservation_vars["start_date"].get(), "Start date", allow_blank=False), "end_date": ensure_date(self.reservation_vars["end_date"].get(), "End date", allow_blank=False),
                "approved_by": self.reservation_vars["approved_by"].get().strip(), "notes": self.reservation_vars["notes"].get().strip(),
            }
            self.db.add_reservation(data); self.refresh_all(); self.clear_vars(self.reservation_vars, keep={"reservation_type": "Event", "bay_count": "1", "start_date": today_str(), "end_date": today_str()}); messagebox.showinfo("Saved", "Reservation saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_temporary_permit(self):
        try:
            data = {
                "permit_holder": self.require(self.temp_vars["permit_holder"].get(), "Permit holder"), "vehicle_reg": normalise_reg(self.require(self.temp_vars["vehicle_reg"].get(), "Vehicle reg")),
                "permit_type": self.temp_vars["permit_type"].get().strip(), "start_date": ensure_date(self.temp_vars["start_date"].get(), "Start date", allow_blank=False), "end_date": ensure_date(self.temp_vars["end_date"].get(), "End date", allow_blank=False),
                "approved_by": self.temp_vars["approved_by"].get().strip(), "reason_recorded": self.temp_vars["reason_recorded"].get().strip(), "notes": self.temp_vars["notes"].get().strip(),
            }
            self.db.add_temporary_permit(data); self.refresh_all(); self.clear_vars(self.temp_vars, keep={"permit_type": "Temporary", "start_date": today_str(), "end_date": today_str()}); messagebox.showinfo("Saved", "Temporary/day permit saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def save_penalty(self):
        try:
            data = {
                "vehicle_reg": normalise_reg(self.require(self.penalty_vars["vehicle_reg"].get(), "Vehicle reg")), "reason": self.penalty_vars["reason"].get().strip(),
                "location": self.require(self.penalty_vars["location"].get(), "Location"), "issued_by": self.require(self.penalty_vars["issued_by"].get(), "Issued by"),
                "external_status": self.penalty_vars["external_status"].get().strip(), "appeal_status": self.penalty_vars["appeal_status"].get().strip(), "notes": self.penalty_vars["notes"].get().strip(),
            }
            self.db.add_penalty(data); self.refresh_all(); self.clear_vars(self.penalty_vars, keep={"reason": "No valid permit", "external_status": "Sent to Workflow Dynamics", "appeal_status": "No Appeal"}); messagebox.showinfo("Saved", "Penalty notice saved.")
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def update_selected_issued_permit(self):
        try:
            permit_id = self.selected_tree_id(self.issued_permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an issued permit first."); return
            self.db.update_issued_permit(permit_id, self.issued_status_var.get(), self.issued_notes_var.get().strip(), float(self.replacement_fee_var.get().strip() or "0"))
            self.refresh_all(); messagebox.showinfo("Updated", "Issued permit updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def update_selected_issued_permit_regs(self):
        try:
            permit_id = self.selected_tree_id(self.issued_permits_tree)
            if not permit_id:
                messagebox.showwarning("No selection", "Please select an issued permit first."); return
            self.db.update_issued_permit_regs(permit_id, self.require(self.new_reg1_var.get(), "New reg 1"), self.new_reg2_var.get().strip())
            self.refresh_all(); self.new_reg1_var.set(""); self.new_reg2_var.set(""); messagebox.showinfo("Updated", "Permit vehicle details updated.")
        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def show_selected_issued_permit(self):
        permit_id = self.selected_tree_id(self.issued_permits_tree)
        if not permit_id:
            messagebox.showwarning("No selection", "Please select an issued permit first."); return
        record = self.db.get_issued_permit(permit_id)
        details = [
            f"Issued Permit #{record['id']}", f"Permit number: {record['permit_number']}", f"Holder: {record['holder_name']}", f"Kind: {record['permit_kind']}",
            f"Scope: {record['campus_scope']}", f"Vehicle reg 1: {record['vehicle_reg_primary']}", f"Vehicle reg 2: {record['vehicle_reg_secondary'] or '-'}",
            f"Issued date: {record['issued_date']}", f"Expiry: {record['expiry_date']}", f"Collection location: {record['collection_location'] or '-'}",
            f"Status: {record['status']}", f"Replacement fee due: £{record['replacement_fee_due']:.2f}", f"Return received: {as_yes_no(bool(record['return_received']))}",
            f"Cancelled at: {record['cancelled_at'] or '-'}", f"Notes: {record['notes'] or '-'}",
        ]
        self.show_text_window(f"Issued permit #{record['id']}", "\n".join(details))

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
    app = CarParkMonitorApp()
    app.mainloop()
