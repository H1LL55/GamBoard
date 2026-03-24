import tkinter as tk
from tkinter import ttk, messagebox

from shared_db import (
    TEMP_PERMIT_OPTIONS,
    ensure_date,
    normalise_reg,
    parse_date,
    today_str,
)
from shared_db import (
    ensure_date,
    normalise_reg,
    parse_car_park_id,
    today_str,
)

from shared_db import (
    TEMP_PERMIT_OPTIONS,
    ensure_date,
    normalise_reg,
    parse_date,
    today_str,
)


class JennaMixin:
    # Jack - work on this file
    # Permit checker, penalties, and shared helper methods.

    def build_temp_permits_tab(self):
        self.temp_permits_tab.columnconfigure(1, weight=1)
        self.temp_permits_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(
            self.temp_permits_tab,
            text="New temporary / day / EV permit",
            padding=12
        )
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(
            self.temp_permits_tab,
            text="Temporary permits",
            padding=8
        )
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

        self.build_form_field(
            form, "Permit holder", 0, self.temp_vars["permit_holder"]
        )
        self.build_form_field(
            form, "Vehicle reg", 1, self.temp_vars["vehicle_reg"]
        )
        self.build_form_field(
            form,
            "Permit type",
            2,
            self.temp_vars["permit_type"],
            widget="combo",
            values=TEMP_PERMIT_OPTIONS
        )
        self.build_form_field(
            form, "Start date", 3, self.temp_vars["start_date"]
        )
        self.build_form_field(
            form, "End date", 4, self.temp_vars["end_date"]
        )
        self.build_form_field(
            form, "Approved by", 5, self.temp_vars["approved_by"]
        )
        self.build_form_field(
            form, "Reason recorded", 6, self.temp_vars["reason_recorded"]
        )
        self.build_form_field(
            form, "Notes", 7, self.temp_vars["notes"]
        )

        ttk.Button(
            form,
            text="Save temporary permit",
            command=self.save_temporary_permit
        ).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        ttk.Button(
            form,
            text="Clear form",
            command=lambda: self.clear_vars(
                self.temp_vars,
                keep={
                    "permit_type": "Temporary",
                    "start_date": today_str(),
                    "end_date": today_str(),
                }
            )
        ).grid(row=9, column=0, columnspan=2, sticky="ew")

        columns = ("ID", "Holder", "Vehicle reg", "Type", "Start", "End", "Status")

        self.temp_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.temp_tree.heading(col, text=col)
            self.temp_tree.column(col, width=130, anchor="center")

        self.temp_tree.column("Holder", width=180, anchor="w")
        self.temp_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.temp_tree.yview
        )
        self.temp_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(
            table_frame,
            text="Refresh",
            command=self.refresh_temp_permits
        ).grid(row=1, column=0, sticky="e", pady=(8, 0))

        ttk.Button(
            table_frame,
            text="Delete selected",
            command=self.delete_selected_temp_permit
        ).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

    def save_temporary_permit(self):
        try:
            data = {
                "permit_holder": self.require(
                    self.temp_vars["permit_holder"].get(),
                    "Permit holder"
                ),
                "vehicle_reg": normalise_reg(
                    self.require(
                        self.temp_vars["vehicle_reg"].get(),
                        "Vehicle reg"
                    )
                ),
                "permit_type": self.temp_vars["permit_type"].get().strip(),
                "start_date": ensure_date(
                    self.temp_vars["start_date"].get(),
                    "Start date",
                    allow_blank=False
                ),
                "end_date": ensure_date(
                    self.temp_vars["end_date"].get(),
                    "End date",
                    allow_blank=False
                ),
                "approved_by": self.temp_vars["approved_by"].get().strip(),
                "reason_recorded": self.temp_vars["reason_recorded"].get().strip(),
                "notes": self.temp_vars["notes"].get().strip(),
            }

            self.db.add_temporary_permit(data)
            self.refresh_all()

            self.clear_vars(
                self.temp_vars,
                keep={
                    "permit_type": "Temporary",
                    "start_date": today_str(),
                    "end_date": today_str(),
                }
            )

            messagebox.showinfo("Saved", "Temporary/day permit saved.")

        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def delete_selected_temp_permit(self):
        # This method deletes the selected temporary permit from the database.

        try:
            # Get the selected temporary permit ID from the table.
            permit_id = self.selected_tree_id(self.temp_tree)

            # If no row is selected, warn the user and stop.
            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select a temporary permit to delete."
                )
                return

            # Ask for confirmation before deleting (safety measure).
            if not messagebox.askyesno(
                "Confirm delete",
                f"Are you sure you want to delete temporary permit {permit_id}?"
            ):
                return

            # Call the database method to delete the temporary permit.
            self.db.delete_temporary_permit(permit_id)

            # Refresh all tables so the deleted data disappears from screen.
            self.refresh_all()

            # Tell the user the action worked.
            messagebox.showinfo("Deleted", "Temporary permit deleted.")

        except Exception as exc:
            # If anything goes wrong, show the error in a popup.
            messagebox.showerror("Could not delete", str(exc))

    def build_checker_tab(self):
        self.checker_tab.columnconfigure(0, weight=1)
        self.checker_tab.rowconfigure(1, weight=1)

        controls = ttk.LabelFrame(
            self.checker_tab,
            text="Patrol check",
            padding=12
        )
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(3, weight=1)

        self.check_reg_var = tk.StringVar()

        ttk.Label(controls, text="Vehicle reg").grid(row=0, column=0, sticky="w")
        ttk.Entry(
            controls,
            textvariable=self.check_reg_var,
            width=20
        ).grid(row=0, column=1, sticky="w", padx=(8, 20))

        ttk.Button(
            controls,
            text="Check vehicle",
            command=self.check_vehicle
        ).grid(row=0, column=2, sticky="e")

        result_frame = ttk.LabelFrame(self.checker_tab, text="Result", padding=8)
        result_frame.grid(row=1, column=0, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.check_result = tk.Text(
            result_frame,
            wrap="word",
            font=("Consolas", 10)
        )
        self.check_result.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.check_result.yview
        )
        self.check_result.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

    def check_vehicle(self):
        try:
            reg = normalise_reg(
                self.require(self.check_reg_var.get(), "Vehicle reg")
            )
            check_date = today_str()

            result = self.db.check_vehicle(reg, check_date)

            lines = [
                f"Vehicle check for {reg}",
                f"Date: {check_date}",
                "-" * 72
            ]

            weekday_name = parse_date(check_date).strftime("%A")

            valid_issued = []
            for permit in result["issued_permits"]:
                if permit["permit_kind"] == "Friday Only" and weekday_name != "Friday":
                    continue
                valid_issued.append(permit)

            if valid_issued:
                lines.append("Issued permit(s) found")
                for permit in valid_issued:
                    lines.append(
                        f"• {permit['permit_number']} | "
                        f"{permit['permit_kind']} | "
                        f"{permit['campus_scope']} | "
                        f"{permit['issued_date']} to {permit['expiry_date']} | "
                        f"status {permit['status']}"
                    )
                lines.append("")
            else:
                lines.append("No active issued permit found for that date.")
                lines.append("")

            if result["temporary_permit"]:
                temp = result["temporary_permit"]
                lines.append("Temporary / day permit found")
                lines.append(f"Holder: {temp['permit_holder']}")
                lines.append(f"Type: {temp['permit_type']}")
                lines.append(
                    f"Valid: {temp['start_date']} to {temp['end_date']}"
                )
                lines.append("")

            if result["visitor"]:
                visitor = result["visitor"]
                lines.append("Visitor booking found")
                lines.append(f"Visitor: {visitor['visitor_name']}")
                lines.append(f"Host: {visitor['host_name']}")
                lines.append(f"Car park: {visitor['car_park']}")
                lines.append("")

            if result["reservation"]:
                reservation = result["reservation"]
                lines.append("Reservation / prior consent found")
                lines.append(f"Reserved for: {reservation['reserved_for']}")
                lines.append(f"Type: {reservation['reservation_type']}")
                lines.append(f"Contact: {reservation['contact_name']}")
                lines.append(f"Car park: {reservation['car_park']}")
                lines.append(
                    f"Dates: {reservation['start_date']} "
                    f"to {reservation['end_date']}"
                )
                lines.append("")

            if (
                not valid_issued
                and not result["temporary_permit"]
                and not result["visitor"]
                and not result["reservation"]
            ):
                lines.append(
                    "No current permit, temporary/day permit, visitor booking or reservation found."
                )
                lines.append(
                    "This vehicle may need further checking by patrol staff."
                )
                lines.append("")

            lines.append("Recent penalty history")

            if result["penalties"]:
                for penalty in result["penalties"]:
                    lines.append(
                        f"• #{penalty['id']} | "
                        f"{penalty['reason']} | "
                        f"{penalty['location']} | "
                        f"{penalty['issued_at']}"
                    )
            else:
                lines.append("• No previous penalty notices recorded.")

            self.check_result.delete("1.0", tk.END)
            self.check_result.insert("1.0", "\n".join(lines))

        except Exception as exc:
            messagebox.showerror("Could not check vehicle", str(exc))

    def build_penalties_tab(self):
        self.penalties_tab.columnconfigure(1, weight=1)
        self.penalties_tab.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(
            self.penalties_tab,
            text="New penalty notice",
            padding=12
        )
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        table_frame = ttk.LabelFrame(
            self.penalties_tab,
            text="Penalty notices",
            padding=8
        )
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

        self.build_form_field(
            form, "Vehicle reg", 0, self.penalty_vars["vehicle_reg"]
        )
        self.build_form_field(
            form,
            "Reason",
            1,
            self.penalty_vars["reason"],
            widget="combo",
            values=[
                "No valid permit",
                "Parked in wrong bay",
                "Overstayed",
                "Unauthorised visitor parking",
                "Incorrect bay use",
                "Other",
            ]
        )
        self.build_form_field(
            form, "Location", 2, self.penalty_vars["location"]
        )
        self.build_form_field(
            form, "Issued by", 3, self.penalty_vars["issued_by"]
        )
        self.build_form_field(
            form,
            "External status",
            4,
            self.penalty_vars["external_status"],
            widget="combo",
            values=[
                "Sent to Workflow Dynamics",
                "Draft",
                "Cancelled",
                "Closed",
            ]
        )
        self.build_form_field(
            form,
            "Appeal status",
            5,
            self.penalty_vars["appeal_status"],
            widget="combo",
            values=[
                "No Appeal",
                "Under Review",
                "Upheld",
                "Cancelled",
            ]
        )
        self.build_form_field(
            form, "Notes", 6, self.penalty_vars["notes"]
        )

        ttk.Button(
            form,
            text="Save penalty notice",
            command=self.save_penalty
        ).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        ttk.Button(
            form,
            text="Clear form",
            command=lambda: self.clear_vars(
                self.penalty_vars,
                keep={
                    "reason": "No valid permit",
                    "external_status": "Sent to Workflow Dynamics",
                    "appeal_status": "No Appeal",
                }
            )
        ).grid(row=8, column=0, columnspan=2, sticky="ew")

        columns = (
            "ID",
            "Vehicle reg",
            "Reason",
            "Location",
            "Issued by",
            "External status",
            "Appeal status",
            "Issued at"
        )

        self.penalties_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.penalties_tree.heading(col, text=col)
            self.penalties_tree.column(col, width=120, anchor="center")

        self.penalties_tree.column("Reason", width=170, anchor="w")
        self.penalties_tree.column("Location", width=150, anchor="w")
        self.penalties_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.penalties_tree.yview
        )
        self.penalties_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(
            table_frame,
            text="Refresh",
            command=self.refresh_penalties
        ).grid(row=1, column=0, sticky="e", pady=(8, 0))

        ttk.Button(
            table_frame,
            text="Delete selected",
            command=self.delete_selected_penalty
        ).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

    def save_penalty(self):
        try:
            data = {
                "vehicle_reg": normalise_reg(
                    self.require(
                        self.penalty_vars["vehicle_reg"].get(),
                        "Vehicle reg"
                    )
                ),
                "reason": self.penalty_vars["reason"].get().strip(),
                "location": self.require(
                    self.penalty_vars["location"].get(),
                    "Location"
                ),
                "issued_by": self.require(
                    self.penalty_vars["issued_by"].get(),
                    "Issued by"
                ),
                "external_status": self.penalty_vars["external_status"].get().strip(),
                "appeal_status": self.penalty_vars["appeal_status"].get().strip(),
                "notes": self.penalty_vars["notes"].get().strip(),
            }

            self.db.add_penalty(data)
            self.refresh_all()

            self.clear_vars(
                self.penalty_vars,
                keep={
                    "reason": "No valid permit",
                    "external_status": "Sent to Workflow Dynamics",
                    "appeal_status": "No Appeal",
                }
            )

            messagebox.showinfo("Saved", "Penalty notice saved.")

        except Exception as exc:
            messagebox.showerror("Could not save", str(exc))

    def delete_selected_penalty(self):
        # This method deletes the selected penalty notice from the database.

        try:
            # Get the selected penalty ID from the table.
            penalty_id = self.selected_tree_id(self.penalties_tree)

            # If no row is selected, warn the user and stop.
            if not penalty_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select a penalty notice to delete."
                )
                return

            # Ask for confirmation before deleting (safety measure).
            if not messagebox.askyesno(
                "Confirm delete",
                f"Are you sure you want to delete penalty {penalty_id}?"
            ):
                return

            # Call the database method to delete the penalty.
            self.db.delete_penalty(penalty_id)

            # Refresh all tables so the deleted data disappears from screen.
            self.refresh_all()

            # Tell the user the action worked.
            messagebox.showinfo("Deleted", "Penalty notice deleted.")

        except Exception as exc:
            # If anything goes wrong, show the error in a popup.
            messagebox.showerror("Could not delete", str(exc))

    def build_form_field(
        self,
        parent,
        label,
        row,
        variable,
        widget="entry",
        values=None
    ):
        ttk.Label(parent, text=label).grid(
            row=row,
            column=0,
            sticky="w",
            pady=3,
            padx=(0, 8)
        )

        if widget == "combo":
            control = ttk.Combobox(
                parent,
                textvariable=variable,
                values=values or [],
                state="readonly",
                width=34
            )
        else:
            control = ttk.Entry(
                parent,
                textvariable=variable,
                width=37
            )

        control.grid(row=row, column=1, sticky="ew", pady=3)
        parent.columnconfigure(1, weight=1)
        return control

    def clear_vars(self, variables, keep=None):
        if keep is None:
            keep = {}

        for key, var in variables.items():
            var.set(keep.get(key, ""))

    def require(self, value, label):
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError(f"{label} is required.")
        return cleaned

    def selected_tree_id(self, tree):
        selected = tree.selection()
        if not selected:
            return None
        return tree.item(selected[0], "values")[0]

    def replace_tree_data(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            tree.insert("", "end", values=tuple(row))