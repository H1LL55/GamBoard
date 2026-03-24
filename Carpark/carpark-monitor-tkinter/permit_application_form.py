import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from shared_db import (
    DB_PATH,
    COLLECTION_LOCATIONS,
    INELIGIBLE_EMPLOYMENT,
    DatabaseManager,
    default_collection_for_campus,
    default_expiry_str,
    ensure_date,
    normalise_reg,
    parse_car_park_id,
    today_str,
)


class PermitApplicationForm(tk.Tk):
    # This file is the applicant side only.
    # The idea is people fill the form in here, and admin staff review it in the dashboard file.
    def __init__(self):
        super().__init__()
        self.title("CCCU Staff Permit Application Form")
        self.geometry("660x960")
        self.minsize(660,700)

        self.db = DatabaseManager(DB_PATH)
        self.car_park_choices = self.db.car_park_options()
        self.terms_file = Path(__file__).with_name("permit_terms.txt")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.build_header()
        self.build_form_area()
        self.clear_form()

    # Main layout
    def build_header(self):
        header = ttk.Frame(self, padding=(16, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="CCCU Staff Parking Permit Application", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Use this form to submit a new permit request. Once saved, it will appear in the admin dashboard.",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def build_form_area(self):
        outer = ttk.Frame(self, padding=(16, 4, 16, 16))
        outer.grid(row=1, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.form_body = ttk.Frame(canvas, padding=4)
        self.form_body.columnconfigure(1, weight=1)

        canvas_window = canvas.create_window((0, 0), window=self.form_body, anchor="nw")

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_embedded_frame(event):
            canvas.itemconfigure(canvas_window, width=event.width)

        self.form_body.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", resize_embedded_frame)

        self.build_form_fields()

    # Form fields and variables
    def build_form_fields(self):
        self.form_vars = {
            "applicant_type": tk.StringVar(value="Staff"),
            "campus": tk.StringVar(value="Canterbury"),
            "full_name": tk.StringVar(),
            "university_id": tk.StringVar(),
            "payroll_number": tk.StringVar(),
            "department": tk.StringVar(),
            "contact_number": tk.StringVar(),
            "email": tk.StringVar(),
            "employment_type": tk.StringVar(value="Salaried"),
            "home_postcode": tk.StringVar(),
            "vehicle_reg": tk.StringVar(),
            "secondary_vehicle_reg": tk.StringVar(),
            "reason": tk.StringVar(),
            "accessibility_needs": tk.StringVar(),
            "distance_km": tk.StringVar(),
            "desired_car_park": tk.StringVar(),
            "valid_from": tk.StringVar(value=today_str()),
            "valid_to": tk.StringVar(value=default_expiry_str()),
            "business_travel_trips": tk.StringVar(value="0"),
            "planned_days": tk.StringVar(),
            "evidence_summary": tk.StringVar(),
            "permit_scope": tk.StringVar(value="Campus default"),
            "collection_location": tk.StringVar(value="Old Sessions House reception"),
        }

        self.blue_badge_var = tk.BooleanVar(value=False)
        self.mobility_need_var = tk.BooleanVar(value=False)
        self.registered_carer_var = tk.BooleanVar(value=False)
        self.child_under_11_var = tk.BooleanVar(value=False)
        self.essential_business_var = tk.BooleanVar(value=False)
        self.business_insurance_var = tk.BooleanVar(value=False)
        self.friday_only_var = tk.BooleanVar(value=False)
        self.accept_terms_var = tk.BooleanVar(value=False)

        row = 0

        details_frame = ttk.LabelFrame(self.form_body, text="Applicant details", padding=12)
        details_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        details_frame.columnconfigure(1, weight=1)
        row += 1

        r = 0
        self.build_form_field(details_frame, "Campus", r, variable=self.form_vars["campus"], widget="combo", values=["Canterbury", "Medway", "Tunbridge Wells"]); r += 1
        self.build_form_field(details_frame, "Full name", r, variable=self.form_vars["full_name"]); r += 1
        self.build_form_field(details_frame, "Payroll no. (staff)", r, variable=self.form_vars["payroll_number"]); r += 1
        self.build_form_field(details_frame, "Department", r, variable=self.form_vars["department"]); r += 1
        self.build_form_field(details_frame, "Contact number", r, variable=self.form_vars["contact_number"]); r += 1
        self.build_form_field(details_frame, "Email", r, variable=self.form_vars["email"]); r += 1
        self.build_form_field(details_frame, "Employment type", r, variable=self.form_vars["employment_type"], widget="combo", values=["Salaried", "Contracted", "Temporary", "Casual", "On Secondment", "KMMS", "Sessional", "Contractor", "Associate", "Self-employed"]); r += 1
        self.build_form_field(details_frame, "Home postcode", r, variable=self.form_vars["home_postcode"])

        vehicle_frame = ttk.LabelFrame(self.form_body, text="Vehicle and permit details", padding=12)
        vehicle_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        vehicle_frame.columnconfigure(1, weight=1)
        row += 1

        r = 0
        self.build_form_field(vehicle_frame, "Vehicle reg 1", r, variable=self.form_vars["vehicle_reg"]); r += 1
        self.build_form_field(vehicle_frame, "Vehicle reg 2", r, variable=self.form_vars["secondary_vehicle_reg"]); r += 1
        self.build_form_field(vehicle_frame, "Reason / justification", r, variable=self.form_vars["reason"]); r += 1
        self.build_form_field(vehicle_frame, "Accessibility / health notes", r, variable=self.form_vars["accessibility_needs"]); r += 1
        self.build_form_field(vehicle_frame, "Distance from campus (km)", r, variable=self.form_vars["distance_km"]); r += 1
        self.build_form_field(vehicle_frame, "Desired car park", r, variable=self.form_vars["desired_car_park"], widget="combo", values=self.car_park_choices); r += 1
        self.build_form_field(vehicle_frame, "Valid from", r, variable=self.form_vars["valid_from"]); r += 1
        self.build_form_field(vehicle_frame, "Valid to", r, variable=self.form_vars["valid_to"]); r += 1
        self.build_form_field(vehicle_frame, "Business travel trips / week", r, variable=self.form_vars["business_travel_trips"]); r += 1
        self.build_form_field(vehicle_frame, "Expected campus days", r, variable=self.form_vars["planned_days"]); r += 1
        self.build_form_field(vehicle_frame, "Additional Comments - Business Travel Only", r, variable=self.form_vars["evidence_summary"]); r += 1
        self.build_form_field(vehicle_frame, "Permit scope", r, variable=self.form_vars["permit_scope"], widget="combo", values=["Campus default", "Canterbury", "Medway only", "Tunbridge Wells only", "Friday only"]); r += 1
        self.build_form_field(vehicle_frame, "Collection location", r, variable=self.form_vars["collection_location"], widget="combo", values=COLLECTION_LOCATIONS)

        criteria_frame = ttk.LabelFrame(self.form_body, text="Eligibility criteria", padding=12)
        criteria_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        criteria_frame.columnconfigure(0, weight=1)
        criteria_frame.columnconfigure(1, weight=1)
        row += 1

        ttk.Checkbutton(criteria_frame, text="Blue Badge holder", variable=self.blue_badge_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Mobility / health condition", variable=self.mobility_need_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Registered carer", variable=self.registered_carer_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Child aged 11 or under", variable=self.child_under_11_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Essential business user", variable=self.essential_business_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Business insurance confirmed", variable=self.business_insurance_var).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(criteria_frame, text="Friday-only permit requested", variable=self.friday_only_var).grid(row=3, column=0, sticky="w")

        notes_frame = ttk.LabelFrame(self.form_body, text="Before submitting", padding=12)
        notes_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        note_text = (
            "• Saving the form does not mean the permit is approved straight away.\n\n"
            "• The application goes into the admin dashboard for review.\n\n"
            "• Staff applications are checked against the eligibility rules from the supplied documents.\n\n"
            "• If a Canterbury application appears to be within 3 miles, it can still be saved but it will need manual review."
        )
        ttk.Label(notes_frame, text=note_text, justify="left", wraplength=760).pack(fill="x")

        terms_frame = ttk.LabelFrame(self.form_body, text="Terms and conditions", padding=12)
        terms_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        terms_frame.columnconfigure(0, weight=1)
        row += 1

        ttk.Label(
            terms_frame,
            text="Please read the terms and conditions before submitting your application.",
            wraplength=760,
            justify="left",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Button(terms_frame, text="Terms and conditions", command=self.show_terms_window).grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Checkbutton(
            terms_frame,
            text="I have read and accept the terms and conditions.",
            variable=self.accept_terms_var,
            command=self.update_submit_state,
        ).grid(row=2, column=0, sticky="w")

        buttons = ttk.Frame(self.form_body)
        buttons.grid(row=row, column=0, sticky="ew", pady=(8, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        self.submit_button = ttk.Button(buttons, text="Submit application", command=self.save_application)
        self.submit_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(buttons, text="Clear form", command=self.clear_form).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # This just keeps the collection point sensible when the campus changes.
        self.form_vars["campus"].trace_add("write", self.on_campus_changed)
        self.update_submit_state()

    # ------------------------------
    # Small form helpers
    # ------------------------------
    def build_form_field(self, parent, label, row, variable, widget="entry", values=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
        if widget == "combo":
            control = ttk.Combobox(parent, textvariable=variable, values=values or [], state="readonly", width=42)
        else:
            control = ttk.Entry(parent, textvariable=variable, width=45)
        control.grid(row=row, column=1, sticky="ew", pady=4)
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

    def load_terms_text(self):
        try:
            return self.terms_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find the terms file: {self.terms_file.name}. Make sure it sits in the same folder as this application file."
            )

    def show_terms_window(self):
        try:
            terms_text = self.load_terms_text()
        except Exception as exc:
            messagebox.showerror("Terms file missing", str(exc))
            return

        window = tk.Toplevel(self)
        window.title("CCCU Parking Permit Terms and Conditions")
        window.geometry("760x620")
        window.minsize(640, 420)
        window.transient(self)
        window.grab_set()

        outer = ttk.Frame(window, padding=12)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="CCCU Parking Permit Terms and Conditions",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        text_frame = ttk.Frame(outer)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_widget = tk.Text(text_frame, wrap="word", font=("Segoe UI", 10), padx=10, pady=10)
        text_widget.grid(row=0, column=0, sticky="nsew")

        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        text_widget.configure(yscrollcommand=text_scroll.set)

        text_widget.insert("1.0", terms_text)
        text_widget.configure(state="disabled")

        ttk.Button(outer, text="Close", command=window.destroy).grid(row=2, column=0, sticky="e", pady=(10, 0))

    def update_submit_state(self):
        if self.accept_terms_var.get():
            self.submit_button.configure(state="normal")
        else:
            self.submit_button.configure(state="disabled")

    def clear_form(self):
        self.clear_vars(
            self.form_vars,
            keep={
                "applicant_type": "Staff",
                "campus": "Canterbury",
                "employment_type": "Salaried",
                "valid_from": today_str(),
                "valid_to": default_expiry_str(),
                "business_travel_trips": "0",
                "permit_scope": "Campus default",
                "collection_location": "Old Sessions House reception",
            },
        )
        for flag in [
            self.blue_badge_var,
            self.mobility_need_var,
            self.registered_carer_var,
            self.child_under_11_var,
            self.essential_business_var,
            self.business_insurance_var,
            self.friday_only_var,
            self.accept_terms_var,
        ]:
            flag.set(False)
        if hasattr(self, "submit_button"):
            self.update_submit_state()

    def on_campus_changed(self, *_):
        campus = self.form_vars["campus"].get().strip()
        self.form_vars["collection_location"].set(default_collection_for_campus(campus))

    # ------------------------------
    # Save logic
    # ------------------------------
    def save_application(self):
        try:
            if not self.accept_terms_var.get():
                raise ValueError("You must read and accept the terms and conditions before submitting the form.")

            campus = self.form_vars["campus"].get().strip()
            applicant_type = self.form_vars["applicant_type"].get().strip()
            employment_type = self.form_vars["employment_type"].get().strip()

            blue_badge = self.blue_badge_var.get()
            mobility_need = self.mobility_need_var.get()
            registered_carer = self.registered_carer_var.get()
            child_under_11 = self.child_under_11_var.get()
            essential_business_user = self.essential_business_var.get()
            business_insurance = self.business_insurance_var.get()
            friday_only = self.friday_only_var.get()

            # Same validation rules as before, just moved into the separate applicant app.
            if applicant_type == "Staff" and employment_type in INELIGIBLE_EMPLOYMENT and not friday_only:
                raise ValueError("This employment type is not eligible for a standard staff permit in the supplied documents.")

            if applicant_type == "Staff" and not any([blue_badge, mobility_need, registered_carer, child_under_11, essential_business_user, friday_only]):
                raise ValueError("Staff applications should match at least one eligibility criterion, or be marked as Friday-only.")

            trips_per_week = int(self.form_vars["business_travel_trips"].get().strip() or "0")
            if essential_business_user and (trips_per_week < 3 or not business_insurance):
                raise ValueError("Essential business users should have at least 3 business trips per week and business insurance recorded.")

            distance = self.form_vars["distance_km"].get().strip()
            distance_km = float(distance) if distance else None

            if applicant_type == "Staff" and campus == "Canterbury" and distance_km is not None and distance_km < 4.83 and not any([blue_badge, mobility_need, essential_business_user, friday_only]):
                messagebox.showwarning("Distance warning", "This Canterbury staff application appears to be within 3 miles. It has still been saved for manual review.")

            data = {
                "applicant_type": applicant_type,
                "campus": campus,
                "full_name": self.require(self.form_vars["full_name"].get(), "Full name"),
                "university_id": self.form_vars["university_id"].get().strip(),
                "payroll_number": self.form_vars["payroll_number"].get().strip(),
                "department": self.form_vars["department"].get().strip(),
                "contact_number": self.form_vars["contact_number"].get().strip(),
                "email": self.require(self.form_vars["email"].get(), "Email"),
                "employment_type": employment_type,
                "home_postcode": self.form_vars["home_postcode"].get().strip(),
                "vehicle_reg": normalise_reg(self.require(self.form_vars["vehicle_reg"].get(), "Vehicle reg 1")),
                "secondary_vehicle_reg": normalise_reg(self.form_vars["secondary_vehicle_reg"].get().strip()),
                "reason": self.form_vars["reason"].get().strip(),
                "accessibility_needs": self.form_vars["accessibility_needs"].get().strip(),
                "distance_km": distance_km,
                "desired_car_park_id": parse_car_park_id(self.form_vars["desired_car_park"].get()),
                "valid_from": ensure_date(self.form_vars["valid_from"].get(), "Valid from"),
                "valid_to": ensure_date(self.form_vars["valid_to"].get(), "Valid to"),
                "blue_badge": blue_badge,
                "mobility_need": mobility_need,
                "registered_carer": registered_carer,
                "child_under_11": child_under_11,
                "essential_business_user": essential_business_user,
                "business_travel_trips": trips_per_week,
                "business_insurance": business_insurance,
                "friday_only_requested": friday_only,
                "planned_days": self.form_vars["planned_days"].get().strip(),
                "evidence_summary": self.form_vars["evidence_summary"].get().strip(),
                "permit_scope": self.form_vars["permit_scope"].get().strip(),
                "collection_location": self.form_vars["collection_location"].get().strip() or default_collection_for_campus(campus),
            }

            self.db.add_permit_application(data)
            self.clear_form()
            messagebox.showinfo("Submitted", "Permit application saved and sent for review.")
        except Exception as exc:
            messagebox.showerror("Could not submit", str(exc))


if __name__ == "__main__":
    app = PermitApplicationForm()
    app.mainloop()
