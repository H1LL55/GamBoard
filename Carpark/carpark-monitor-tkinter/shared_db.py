import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path


# Store the database in the same folder as this file
DB_PATH = Path(__file__).with_name("carpark_monitor.db")


# Starting car park data
CAR_PARK_SEED = [
    {"campus": "Canterbury", "name": "Verena Holmes Undercroft",                "standard_bays": 12,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 10, "department_bays": 0, "total_bays": 25},
    {"campus": "Canterbury", "name": "Black Car Park (Verena Holmes)",          "standard_bays": 63,  "visitor_bays": 2,  "short_stay_bays": 0, "electric_charging": 10, "disabled_bays": 5, "contractor_bays": 9, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 89},
    {"campus": "Canterbury", "name": "Vernon Place",                            "standard_bays": 7,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 8},
    {"campus": "Canterbury", "name": "Red Car Park (North Holmes Road)",        "standard_bays": 29,  "visitor_bays": 4,  "short_stay_bays": 2, "electric_charging": 2,  "disabled_bays": 7, "contractor_bays": 0, "motorcycle_bays": 1,  "department_bays": 8, "total_bays": 53},
    {"campus": "Canterbury", "name": "Green Car Park (Governor's Hse)",         "standard_bays": 32,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 33},
    {"campus": "Canterbury", "name": "St Martins Priory",                       "standard_bays": 22,  "visitor_bays": 8,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 5, "total_bays": 37},
    {"campus": "Canterbury", "name": "Augustine House",                         "standard_bays": 5,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 2, "total_bays": 7},
    {"campus": "Canterbury", "name": "St. George's Student Union",              "standard_bays": 0,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 2, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 2},
    {"campus": "Canterbury", "name": "Yellow Car Park (St. Gregory's) approx",  "standard_bays": 41,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 41},
    {"campus": "Canterbury", "name": "TOSH Visitors Car Park",                  "standard_bays": 0,   "visitor_bays": 15, "short_stay_bays": 1, "electric_charging": 2,  "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 2, "total_bays": 21},
    {"campus": "Canterbury", "name": "Mauve Car Park (TOSH)",                   "standard_bays": 9,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 9},
    {"campus": "Canterbury", "name": "Grey Car Park (Prison)",                  "standard_bays": 44,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 6, "total_bays": 53},
    {"campus": "Canterbury", "name": "Sports Centre",                           "standard_bays": 7,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 3, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 10},
    {"campus": "Medway", "name": "Rowan Williams Court",                        "standard_bays": 121, "visitor_bays": 30, "short_stay_bays": 0, "electric_charging": 2,  "disabled_bays": 4, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 4, "total_bays": 157},
    {"campus": "Medway", "name": "Cathedral Court",                             "standard_bays": 88,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 1, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 1, "total_bays": 89},
    {"campus": "Medway", "name": "North Road",                                  "standard_bays": 15,  "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 0,  "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 15},
    {"campus": "Tunbridge Wells", "name": "Salomons / Meadow Road",             "standard_bays": 0,   "visitor_bays": 0,  "short_stay_bays": 0, "electric_charging": 2,  "disabled_bays": 0, "contractor_bays": 0, "motorcycle_bays": 0,  "department_bays": 0, "total_bays": 2},
]


# Policy and form options
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
    "Active",
    "Inactive",
    "Lost",
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


# ---------------------------
# Helper functions
# ---------------------------

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

    if value == "":
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
        first_part = str(value).split(" - ", 1)[0]
        return int(first_part)
    except (TypeError, ValueError) as exc:
        raise ValueError("Please choose a valid car park.") from exc


def normalise_reg(reg):
    reg = (reg or "").upper()
    reg = " ".join(reg.split())
    return reg


def as_yes_no(flag: bool) -> str:
    if flag:
        return "Yes"
    return "No"


def today_plus_days(days: int) -> str:
    future_date = date.today() + timedelta(days=days)
    return future_date.isoformat()


def default_collection_for_campus(campus: str) -> str:
    mapping = {
        "Canterbury": "Old Sessions House reception",
        "Medway": "Medway reception",
        "Tunbridge Wells": "Tunbridge Wells reception",
    }
    return mapping.get(campus or "", "Old Sessions House reception")


# ---------------------------
# Database manager
# ---------------------------

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
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        columns = set()

        for row in rows:
            columns.add(row["name"])

        return columns

    def add_column_if_missing(self, conn, table, column_def):
        column_name = column_def.split()[0]
        columns = self.table_columns(conn, table)

        if column_name not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")

    def migrate(self, conn):
        permit_application_columns = [
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
        ]

        for column_def in permit_application_columns:
            self.add_column_if_missing(conn, "permit_applications", column_def)

        visitor_columns = [
            "booked_in_advance INTEGER NOT NULL DEFAULT 1",
            "permit_issued_in_advance INTEGER NOT NULL DEFAULT 1",
        ]
        for column_def in visitor_columns:
            self.add_column_if_missing(conn, "visitor_bookings", column_def)

        reservation_columns = ["approved_by TEXT"]
        for column_def in reservation_columns:
            self.add_column_if_missing(conn, "reservations", column_def)

        temporary_permit_columns = ["approved_by TEXT", "reason_recorded TEXT"]
        for column_def in temporary_permit_columns:
            self.add_column_if_missing(conn, "temporary_permits", column_def)

        penalty_columns = [
            "amount_full REAL NOT NULL DEFAULT 70",
            "amount_discounted REAL NOT NULL DEFAULT 35",
            "discount_deadline TEXT",
        ]
        for column_def in penalty_columns:
            self.add_column_if_missing(conn, "penalties", column_def)

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

    # ---------------------------
    # Shared lookups
    # ---------------------------

    def fetch_car_parks(self):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM car_parks ORDER BY campus, name"
            ).fetchall()
            return rows

    def car_park_options(self):
        options = []
        rows = self.fetch_car_parks()

        for row in rows:
            option = f"{row['id']} - {row['campus']} - {row['name']}"
            options.append(option)

        return options

    # ---------------------------
    # Permit applications
    # ---------------------------

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
                    data["applicant_type"],
                    data["campus"],
                    data["full_name"],
                    data["university_id"],
                    data["payroll_number"],
                    data["email"],
                    data["department"],
                    data["contact_number"],
                    data["home_postcode"],
                    data["employment_type"],
                    data["vehicle_reg"],
                    data["secondary_vehicle_reg"],
                    data["reason"],
                    data["accessibility_needs"],
                    data["distance_km"],
                    data["desired_car_park_id"],
                    data["valid_from"],
                    data["valid_to"],
                    "Pending HoD Review",
                    "",
                    now_str(),
                    int(data["blue_badge"]),
                    int(data["mobility_need"]),
                    int(data["registered_carer"]),
                    int(data["child_under_11"]),
                    int(data["essential_business_user"]),
                    data["business_travel_trips"],
                    int(data["business_insurance"]),
                    int(data["friday_only_requested"]),
                    data["planned_days"],
                    data["evidence_summary"],
                    data["permit_scope"],
                    data["collection_location"],
                    "Pending",
                    "Pending",
                    "No Appeal",
                ),
            )

    def list_permit_applications(self):
        with self.connect() as conn:
            rows = conn.execute(
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
            return rows

    def get_permit_application(self, permit_id):
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT p.*, COALESCE(c.name, '') AS car_park_name
                FROM permit_applications p
                LEFT JOIN car_parks c ON c.id = p.desired_car_park_id
                WHERE p.id = ?
                """,
                (permit_id,),
            ).fetchone()
            return row

    def update_permit_status(self, permit_id, status, reviewer_name, notes):
        with self.connect() as conn:
            fields = {}
            fields["status"] = status
            fields["reviewer_notes"] = notes

            if status == "Awaiting SMT Approval":
                fields["head_recommendation"] = "Supported"
                fields["head_recommended_by"] = reviewer_name
                fields["head_recommendation_date"] = today_str()

            elif status == "Approved":
                fields["smt_decision"] = "Approved"
                fields["smt_decided_by"] = reviewer_name
                fields["smt_decision_date"] = today_str()

            elif status == "Declined":
                fields["smt_decision"] = "Declined"
                fields["smt_decided_by"] = reviewer_name
                fields["smt_decision_date"] = today_str()

            elif status.startswith("Appeal"):
                fields["appeal_status"] = status

            assignment_parts = []
            values = []

            for key, value in fields.items():
                assignment_parts.append(f"{key} = ?")
                values.append(value)

            assignments = ", ".join(assignment_parts)
            values.append(permit_id)

            conn.execute(
                f"UPDATE permit_applications SET {assignments} WHERE id = ?",
                values
            )

    # ---------------------------
    # Issued permits
    # ---------------------------

    def next_permit_number(self, conn):
        count = conn.execute("SELECT COUNT(*) FROM issued_permits").fetchone()[0]
        count = count + 1
        year = date.today().year
        return f"CCCU-P-{year}-{count:04d}"

    def issue_permit_from_application(self, application_id, permit_kind, campus_scope, expiry_date, collection_location, notes):
        with self.connect() as conn:
            app = conn.execute(
                "SELECT * FROM permit_applications WHERE id = ?",
                (application_id,)
            ).fetchone()

            if not app:
                raise ValueError("Permit application not found.")

            if app["status"] != "Approved":
                raise ValueError("Only approved applications can be issued as permits.")

            existing = conn.execute(
                """
                SELECT id
                FROM issued_permits
                WHERE application_id = ?
                  AND status NOT IN ('Cancelled', 'Returned')
                """,
                (application_id,),
            ).fetchone()

            if existing:
                raise ValueError("A live issued permit already exists for this application.")

            final_campus_scope = campus_scope or app["campus"]
            final_collection_location = (
                collection_location
                or app["collection_location"]
                or default_collection_for_campus(app["campus"])
            )

            issue_reason = app["reason"]
            if not issue_reason:
                issue_reason = "Issued from approved application"

            conn.execute(
                """
                INSERT INTO issued_permits (
                    application_id, permit_number, permit_kind, campus_scope, holder_name,
                    vehicle_reg_primary, vehicle_reg_secondary, issue_reason, issued_date,
                    expiry_date, collection_location, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    self.next_permit_number(conn),
                    permit_kind,
                    final_campus_scope,
                    app["full_name"],
                    app["vehicle_reg"],
                    app["secondary_vehicle_reg"],
                    issue_reason,
                    today_str(),
                    expiry_date,
                    final_collection_location,
                    "Ready for Collection",
                    notes,
                    now_str(),
                ),
            )

    def list_issued_permits(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, permit_number, holder_name, permit_kind, campus_scope,
                       vehicle_reg_primary, COALESCE(vehicle_reg_secondary, '') AS vehicle_reg_secondary,
                       issued_date, expiry_date, status
                FROM issued_permits
                ORDER BY id DESC
                """
            ).fetchall()
            return rows

    def get_issued_permit(self, permit_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM issued_permits WHERE id = ?",
                (permit_id,)
            ).fetchone()
            return row

    def update_issued_permit(self, permit_id, status, notes, replacement_fee_due=0):
        with self.connect() as conn:
            fields = {}
            fields["status"] = status
            fields["notes"] = notes
            fields["replacement_fee_due"] = replacement_fee_due

            if status in {"Cancelled", "Returned"}:
                fields["cancelled_at"] = now_str()

            if status == "Returned":
                fields["return_received"] = 1

            assignment_parts = []
            values = []

            for key, value in fields.items():
                assignment_parts.append(f"{key} = ?")
                values.append(value)

            assignments = ", ".join(assignment_parts)
            values.append(permit_id)

            conn.execute(
                f"UPDATE issued_permits SET {assignments} WHERE id = ?",
                values
            )

    def update_issued_permit_regs(self, permit_id, reg1, reg2):
        with self.connect() as conn:
            primary_reg = normalise_reg(reg1)

            if reg2:
                secondary_reg = normalise_reg(reg2)
            else:
                secondary_reg = ""

            update_note = f"\n[{now_str()}] Vehicle details updated."

            conn.execute(
                """
                UPDATE issued_permits
                SET vehicle_reg_primary = ?, vehicle_reg_secondary = ?, notes = COALESCE(notes, '') || ?
                WHERE id = ?
                """,
                (primary_reg, secondary_reg, update_note, permit_id),
            )

    # ---------------------------
    # Visitors
    # ---------------------------

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
                    int(data["booked_in_advance"]),
                    int(data["permit_issued_in_advance"]),
                ),
            )

    def list_visitor_bookings(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT v.id, v.visitor_name, v.host_name, v.vehicle_reg, v.visit_date,
                       v.space_required, COALESCE(c.name, '') AS car_park, v.status
                FROM visitor_bookings v
                LEFT JOIN car_parks c ON c.id = v.car_park_id
                ORDER BY v.visit_date DESC, v.id DESC
                """
            ).fetchall()
            return rows

    # ---------------------------
    # Reservations
    # ---------------------------

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
                    data["approved_by"],
                ),
            )

    def list_reservations(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT r.id, r.reserved_for, r.reservation_type, r.contact_name,
                       COALESCE(r.vehicle_reg, '') AS vehicle_reg, r.start_date, r.end_date,
                       r.bay_count, COALESCE(c.name, '') AS car_park, r.status
                FROM reservations r
                LEFT JOIN car_parks c ON c.id = r.car_park_id
                ORDER BY r.start_date DESC, r.id DESC
                """
            ).fetchall()
            return rows

    # ---------------------------
    # Temporary permits
    # ---------------------------

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
                    data["permit_holder"],
                    data["vehicle_reg"],
                    data["permit_type"],
                    data["start_date"],
                    data["end_date"],
                    "Active",
                    data["notes"],
                    now_str(),
                    data["approved_by"],
                    data["reason_recorded"],
                ),
            )

    def list_temporary_permits(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, permit_holder, vehicle_reg, permit_type, start_date, end_date, status
                FROM temporary_permits
                ORDER BY start_date DESC, id DESC
                """
            ).fetchall()
            return rows

    # ---------------------------
    # Penalties
    # ---------------------------

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
                    data["vehicle_reg"],
                    data["reason"],
                    data["location"],
                    data["issued_by"],
                    data["external_status"],
                    data["appeal_status"],
                    data["notes"],
                    now_str(),
                    70,
                    35,
                    today_plus_days(14),
                ),
            )

    def list_penalties(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, vehicle_reg, reason, location, issued_by,
                       external_status, appeal_status, issued_at
                FROM penalties
                ORDER BY id DESC
                """
            ).fetchall()
            return rows

    # ---------------------------
    # Dashboard numbers
    # ---------------------------

    def dashboard_counts(self):
        with self.connect() as conn:
            today = today_str()

            car_parks = conn.execute(
                "SELECT COUNT(*) FROM car_parks"
            ).fetchone()[0]

            total_spaces = conn.execute(
                "SELECT COALESCE(SUM(total_bays),0) FROM car_parks WHERE campus='Canterbury'"
            ).fetchone()[0]

            pending_permits = conn.execute(
                """
                SELECT COUNT(*)
                FROM permit_applications
                WHERE status IN ('Pending HoD Review', 'Awaiting SMT Approval')
                """
            ).fetchone()[0]

            approved_permits = conn.execute(
                "SELECT COUNT(*) FROM permit_applications WHERE status='Approved'"
            ).fetchone()[0]

            issued_permits = conn.execute(
                """
                SELECT COUNT(*)
                FROM issued_permits
                WHERE status NOT IN ('Cancelled', 'Returned')
                """
            ).fetchone()[0]

            friday_only = conn.execute(
                """
                SELECT COUNT(*)
                FROM issued_permits
                WHERE permit_kind='Friday Only'
                  AND status NOT IN ('Cancelled', 'Returned')
                """
            ).fetchone()[0]

            today_visitors = conn.execute(
                "SELECT COUNT(*) FROM visitor_bookings WHERE visit_date = ?",
                (today,),
            ).fetchone()[0]

            active_reservations = conn.execute(
                """
                SELECT COUNT(*)
                FROM reservations
                WHERE status='Active'
                  AND start_date <= ?
                  AND end_date >= ?
                """,
                (today, today),
            ).fetchone()[0]

            active_temporary_permits = conn.execute(
                """
                SELECT COUNT(*)
                FROM temporary_permits
                WHERE status='Active'
                  AND start_date <= ?
                  AND end_date >= ?
                """,
                (today, today),
            ).fetchone()[0]

            penalties = conn.execute(
                "SELECT COUNT(*) FROM penalties"
            ).fetchone()[0]

            return {
                "car_parks": car_parks,
                "total_spaces": total_spaces,
                "pending_permits": pending_permits,
                "approved_permits": approved_permits,
                "issued_permits": issued_permits,
                "friday_only": friday_only,
                "today_visitors": today_visitors,
                "active_reservations": active_reservations,
                "active_temporary_permits": active_temporary_permits,
                "penalties": penalties,
            }

    # ---------------------------
    # Vehicle check
    # ---------------------------

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

            return {
                "issued_permits": issued,
                "temporary_permit": temp_permit,
                "visitor": visitor,
                "reservation": reservation,
                "penalties": penalties,
            }