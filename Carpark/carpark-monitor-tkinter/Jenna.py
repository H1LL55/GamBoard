import tkinter as tk
from tkinter import ttk

from Callum import CallumMixin
from Kris import KrisMixin
from Paris import ParisMixin
from Jack import JackMixin

from shared_db import (
    ensure_date,
    normalise_reg,
    parse_car_park_id,
    today_str,
)


class JennaMixin:
    # Jenna - work on this file
    # Visitor bookings and reservations.

    def build_visitors_tab(self):
        self.visitors_tab.columnconfigure(1, weight=1)
        self.visitors_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(
            self.visitors_tab,
            text="New visitor booking",
            padding=12
        )
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(
            self.visitors_tab,
            text="Visitor bookings",
            padding=8
        )
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

        self.build_form_field(
            form, "Visitor name", 0, self.visitor_vars["visitor_name"]
        )
        self.build_form_field(
            form, "Host name", 1, self.visitor_vars["host_name"]
        )
        self.build_form_field(
            form, "Host department", 2, self.visitor_vars["host_department"]
        )
        self.build_form_field(
            form, "Email", 3, self.visitor_vars["email"]
        )
        self.build_form_field(
            form, "Vehicle reg", 4, self.visitor_vars["vehicle_reg"]
        )
        self.build_form_field(
            form, "Visit date", 5, self.visitor_vars["visit_date"]
        )
        self.build_form_field(
            form,
            "Car park",
            6,
            self.visitor_vars["car_park"],
            widget="combo",
            values=self.car_park_choices
        )
        self.build_form_field(
            form, "Spaces required", 7, self.visitor_vars["space_required"]
        )
        self.build_form_field(
            form, "Notes", 8, self.visitor_vars["notes"]
        )

        ttk.Checkbutton(
            form,
            text="Booked in advance",
            variable=self.visitor_booked_advance_var
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Checkbutton(
            form,
            text="Permit issued in advance",
            variable=self.visitor_permit_advance_var
        ).grid(row=10, column=0, columnspan=2, sticky="w")

        ttk.Button(
            form,
            text="Save booking",
            command=self.save_visitor_booking
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        ttk.Button(
            form,
            text="Clear form",
            command=lambda: self.clear_vars(
                self.visitor_vars,
                keep={
                    "visit_date": today_str(),
                    "space_required": "1"
                }
            )
        ).grid(row=12, column=0, columnspan=2, sticky="ew")

        columns = (
            "ID",
            "Visitor",
            "Host",
            "Vehicle reg",
            "Visit date",
            "Spaces",
            "Car park",
            "Status"
        )

        self.visitors_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.visitors_tree.heading(col, text=col)
            self.visitors_tree.column(col, width=120, anchor="center")

        self.visitors_tree.column("Visitor", width=160, anchor="w")
        self.visitors_tree.column("Host", width=160, anchor="w")
        self.visitors_tree.column("Car park", width=220, anchor="w")
        self.visitors_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.visitors_tree.yview
        )
        self.visitors_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(
            table_frame,
            text="Refresh",
            command=self.refresh_visitors
        ).grid(row=1, column=0, sticky="e", pady=(8, 0))

    def save_visitor_booking(self):
        try:
            data = {
                "visitor_name": self.require(
                    self.visitor_vars["visitor_name"].get(),
                    "Visitor name"
                ),
                "host_name": self.require(
                    self.visitor_vars["host_name"].get(),
                    "Host name"
                ),
                "host_department": self.visitor_vars["host_department"].get().strip(),
                "email": self.require(
                    self.visitor_vars["email"].get(),
                    "Email"
                ),
                "vehicle_reg": normalise_reg(
                    self.require(
                        self.visitor_vars["vehicle_reg"].get(),
                        "Vehicle reg"
                    )
                ),
                "visit_date": ensure_date(
                    self.visitor_vars["visit_date"].get(),
                    "Visit date",
                    allow_blank=False
                ),
                "car_park_id": parse_car_park_id(
                    self.visitor_vars["car_park"].get()
                ),
                "space_required": int(
                    self.visitor_vars["space_required"].get().strip() or "1"
                ),
                "notes": self.visitor_vars["notes"].get().strip(),
                "booked_in_advance": self.visitor_booked_advance_var.get(),
                "permit_issued_in_advance": self.visitor_permit_advance_var.get(),
            }

            self.db.add_visitor_booking(data)
            self.refresh_all()

            self.clear_vars(
                self.visitor_vars,
                keep={
                    "visit_date": today_str(),
                    "space_required": "1"
                }
            )

            self.visitor_booked_advance_var.set(True)
            self.visitor_permit_advance_var.set(True)

            messagebox.showinfo("Saved", "Visitor booking saved.")

        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def build_reservations_tab(self):
        self.reservations_tab.columnconfigure(1, weight=1)
        self.reservations_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(
            self.reservations_tab,
            text="New reservation / prior consent",
            padding=12
        )
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(
            self.reservations_tab,
            text="Reservations",
            padding=8
        )
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

        self.build_form_field(
            form, "Reserved for", 0, self.reservation_vars["reserved_for"]
        )
        self.build_form_field(
            form,
            "Reservation type",
            1,
            self.reservation_vars["reservation_type"],
            widget="combo",
            values=["Event", "Contractor", "Guest", "VIP", "Short Stay", "Other"]
        )
        self.build_form_field(
            form, "Contact name", 2, self.reservation_vars["contact_name"]
        )
        self.build_form_field(
            form, "Vehicle reg", 3, self.reservation_vars["vehicle_reg"]
        )
        self.build_form_field(
            form,
            "Car park",
            4,
            self.reservation_vars["car_park"],
            widget="combo",
            values=self.car_park_choices
        )
        self.build_form_field(
            form, "Bay count", 5, self.reservation_vars["bay_count"]
        )
        self.build_form_field(
            form, "Start date", 6, self.reservation_vars["start_date"]
        )
        self.build_form_field(
            form, "End date", 7, self.reservation_vars["end_date"]
        )
        self.build_form_field(
            form,
            "Approved / consent by",
            8,
            self.reservation_vars["approved_by"]
        )
        self.build_form_field(
            form, "Notes", 9, self.reservation_vars["notes"]
        )

        ttk.Button(
            form,
            text="Save reservation",
            command=self.save_reservation
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        ttk.Button(
            form,
            text="Clear form",
            command=lambda: self.clear_vars(
                self.reservation_vars,
                keep={
                    "reservation_type": "Event",
                    "bay_count": "1",
                    "start_date": today_str(),
                    "end_date": today_str(),
                }
            )
        ).grid(row=11, column=0, columnspan=2, sticky="ew")

        columns = (
            "ID",
            "Reserved for",
            "Type",
            "Contact",
            "Vehicle reg",
            "Start",
            "End",
            "Bays",
            "Car park",
            "Status"
        )

        self.reservations_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.reservations_tree.heading(col, text=col)
            self.reservations_tree.column(col, width=110, anchor="center")

        self.reservations_tree.column("Reserved for", width=160, anchor="w")
        self.reservations_tree.column("Contact", width=150, anchor="w")
        self.reservations_tree.column("Car park", width=220, anchor="w")
        self.reservations_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.reservations_tree.yview
        )
        self.reservations_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(
            table_frame,
            text="Refresh",
            command=self.refresh_reservations
        ).grid(row=1, column=0, sticky="e", pady=(8, 0))

    def save_reservation(self):
        try:
            reg_value = self.reservation_vars["vehicle_reg"].get().strip()

            if reg_value:
                reg_value = normalise_reg(reg_value)
            else:
                reg_value = ""

            data = {
                "reserved_for": self.require(
                    self.reservation_vars["reserved_for"].get(),
                    "Reserved for"
                ),
                "reservation_type": self.reservation_vars["reservation_type"].get().strip(),
                "contact_name": self.require(
                    self.reservation_vars["contact_name"].get(),
                    "Contact name"
                ),
                "vehicle_reg": reg_value,
                "car_park_id": parse_car_park_id(
                    self.reservation_vars["car_park"].get()
                ),
                "bay_count": int(
                    self.reservation_vars["bay_count"].get().strip() or "1"
                ),
                "start_date": ensure_date(
                    self.reservation_vars["start_date"].get(),
                    "Start date",
                    allow_blank=False
                ),
                "end_date": ensure_date(
                    self.reservation_vars["end_date"].get(),
                    "End date",
                    allow_blank=False
                ),
                "approved_by": self.reservation_vars["approved_by"].get().strip(),
                "notes": self.reservation_vars["notes"].get().strip(),
            }

            self.db.add_reservation(data)
            self.refresh_all()

            self.clear_vars(
                self.reservation_vars,
                keep={
                    "reservation_type": "Event",
                    "bay_count": "1",
                    "start_date": today_str(),
                    "end_date": today_str(),
                }
            )

            messagebox.showinfo("Saved", "Reservation saved.")

        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))