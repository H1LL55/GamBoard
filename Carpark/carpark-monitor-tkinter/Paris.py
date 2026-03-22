import tkinter as tk
from tkinter import ttk, messagebox

from shared_db import (
    COLLECTION_LOCATIONS,
    ISSUED_PERMIT_STATUSES,
    PERMIT_APP_STATUSES,
    PERMIT_KIND_OPTIONS,
    as_yes_no,
    default_expiry_str,
    ensure_date,
)
from shared_db import (
    COLLECTION_LOCATIONS,
    ISSUED_PERMIT_STATUSES,
    PERMIT_APP_STATUSES,
    PERMIT_KIND_OPTIONS,
    as_yes_no,
    default_expiry_str,
    ensure_date,
)


class ParisMixin:
    # Paris - work on this file
    # Permit applications tab and issued permits tab.

    def build_permits_tab(self):
        self.permits_tab.columnconfigure(0, weight=1)
        self.permits_tab.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(
            self.permits_tab,
            text="Applications and review",
            padding=8
        )
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        permit_columns = (
            "ID",
            "Type",
            "Campus",
            "Name",
            "Reg 1",
            "Reg 2",
            "Employment",
            "Email",
            "Car park",
            "Status",
            "Created"
        )

        self.permits_tree = ttk.Treeview(
            table_frame,
            columns=permit_columns,
            show="headings",
            height=20
        )

        for col in permit_columns:
            self.permits_tree.heading(col, text=col)
            self.permits_tree.column(col, width=110, anchor="center")

        self.permits_tree.column("Name", width=160, anchor="w")
        self.permits_tree.column("Email", width=190, anchor="w")
        self.permits_tree.column("Car park", width=220, anchor="w")
        self.permits_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.permits_tree.yview
        )
        self.permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        review = ttk.Frame(table_frame)
        review.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        for i in range(9):
            if i in {3, 5, 6}:
                review.columnconfigure(i, weight=1)
            else:
                review.columnconfigure(i, weight=0)

        ttk.Label(review, text="Review status").grid(
            row=0, column=0, sticky="w"
        )

        self.permit_status_var = tk.StringVar(value="Awaiting SMT Approval")
        ttk.Combobox(
            review,
            textvariable=self.permit_status_var,
            values=PERMIT_APP_STATUSES,
            state="readonly",
            width=22
        ).grid(row=0, column=1, sticky="w", padx=(8, 12))

        ttk.Label(review, text="Reviewer").grid(row=0, column=2, sticky="w")
        self.permit_reviewer_var = tk.StringVar()
        ttk.Entry(
            review,
            textvariable=self.permit_reviewer_var,
            width=16
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(review, text="Notes").grid(row=0, column=4, sticky="w")
        self.permit_review_notes = tk.StringVar()
        ttk.Entry(
            review,
            textvariable=self.permit_review_notes
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        ttk.Button(
            review,
            text="Update selected",
            command=self.update_selected_permit_status
        ).grid(row=0, column=6, sticky="ew")

        ttk.Button(
            review,
            text="View selected",
            command=self.show_selected_permit_details
        ).grid(row=0, column=7, sticky="ew", padx=(8, 12))

        ttk.Button(
            review,
            text="Refresh",
            command=self.refresh_permits
        ).grid(row=0, column=8, sticky="ew")

        issue_frame = ttk.Frame(table_frame)
        issue_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        for i in range(8):
            if i in {1, 3, 5}:
                issue_frame.columnconfigure(i, weight=1)
            else:
                issue_frame.columnconfigure(i, weight=0)

        ttk.Label(issue_frame, text="Issue permit kind").grid(
            row=0, column=0, sticky="w"
        )
        self.issue_permit_kind_var = tk.StringVar(value="Standard")
        ttk.Combobox(
            issue_frame,
            textvariable=self.issue_permit_kind_var,
            values=PERMIT_KIND_OPTIONS,
            state="readonly",
            width=18
        ).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        ttk.Label(issue_frame, text="Scope").grid(row=0, column=2, sticky="w")
        self.issue_scope_var = tk.StringVar(value="")
        ttk.Entry(
            issue_frame,
            textvariable=self.issue_scope_var
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(issue_frame, text="Expiry").grid(row=0, column=4, sticky="w")
        self.issue_expiry_var = tk.StringVar(value=default_expiry_str())
        ttk.Entry(
            issue_frame,
            textvariable=self.issue_expiry_var,
            width=14
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        self.issue_collection_var = tk.StringVar(
            value="Old Sessions House reception"
        )
        ttk.Combobox(
            issue_frame,
            textvariable=self.issue_collection_var,
            values=COLLECTION_LOCATIONS,
            state="readonly",
            width=24
        ).grid(row=0, column=6, sticky="ew", padx=(0, 12))

        ttk.Button(
            issue_frame,
            text="Issue from selected approved application",
            command=self.issue_selected_permit
        ).grid(row=0, column=7, sticky="ew")

    def update_selected_permit_status(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)

            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select a permit application first."
                )
                return

            reviewer = self.require(
                self.permit_reviewer_var.get(),
                "Reviewer"
            )

            self.db.update_permit_status(
                permit_id,
                self.permit_status_var.get(),
                reviewer,
                self.permit_review_notes.get().strip()
            )

            self.refresh_all()
            messagebox.showinfo("Updated", "Permit status updated.")

        except Exception as exc:
            messagebox.showerror("Could not update", str(exc))

    def issue_selected_permit(self):
        try:
            permit_id = self.selected_tree_id(self.permits_tree)

            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select an approved application first."
                )
                return

            expiry = ensure_date(
                self.issue_expiry_var.get(),
                "Issue expiry",
                allow_blank=False
            )

            self.db.issue_permit_from_application(
                permit_id,
                self.issue_permit_kind_var.get().strip(),
                self.issue_scope_var.get().strip(),
                expiry,
                self.issue_collection_var.get().strip(),
                self.permit_review_notes.get().strip(),
            )

            self.refresh_all()
            messagebox.showinfo(
                "Issued",
                "Permit created and marked ready for collection."
            )

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

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=text_box.yview
        )
        scroll.pack(side="right", fill="y")

        text_box.configure(yscrollcommand=scroll.set)
        text_box.insert("1.0", text)
        text_box.configure(state="disabled")

    def show_selected_permit_details(self):
        permit_id = self.selected_tree_id(self.permits_tree)

        if not permit_id:
            messagebox.showwarning(
                "No selection",
                "Please select an application first."
            )
            return

        record = self.db.get_permit_application(permit_id)

        details = [
            f"Application #{record['id']}",
            f"Applicant: {record['full_name']} ({record['applicant_type']})",
            f"Campus: {record['campus']}",
            f"Email: {record['email']}",
            f"Department: {record['department'] or '-'}",
            f"Payroll / University ID: "
            f"{record['payroll_number'] or record['university_id'] or '-'}",
            f"Contact number: {record['contact_number'] or '-'}",
            f"Employment type: {record['employment_type'] or '-'}",
            f"Home postcode: {record['home_postcode'] or '-'}",
            f"Vehicle reg 1: {record['vehicle_reg']}",
            f"Vehicle reg 2: {record['secondary_vehicle_reg'] or '-'}",
            f"Desired car park: {record['car_park_name'] or '-'}",
            f"Requested dates: {record['valid_from'] or '-'} "
            f"to {record['valid_to'] or '-'}",
            "",
            "Eligibility flags",
            f"  Blue Badge: {as_yes_no(bool(record['blue_badge']))}",
            f"  Mobility / health condition: "
            f"{as_yes_no(bool(record['mobility_need']))}",
            f"  Registered carer: "
            f"{as_yes_no(bool(record['registered_carer']))}",
            f"  Child 11 or under: "
            f"{as_yes_no(bool(record['child_under_11']))}",
            f"  Essential business user: "
            f"{as_yes_no(bool(record['essential_business_user']))}",
            f"  Business travel trips/week: "
            f"{record['business_travel_trips']}",
            f"  Business insurance: "
            f"{as_yes_no(bool(record['business_insurance']))}",
            f"  Friday-only requested: "
            f"{as_yes_no(bool(record['friday_only_requested']))}",
            "",
            f"Reason: {record['reason'] or '-'}",
            f"Accessibility / health notes: "
            f"{record['accessibility_needs'] or '-'}",
            f"Evidence summary: {record['evidence_summary'] or '-'}",
            f"Planned days: {record['planned_days'] or '-'}",
            f"Permit scope: {record['permit_scope'] or '-'}",
            f"Collection location: {record['collection_location'] or '-'}",
            "",
            "Authorisation",
            f"Status: {record['status']}",
            f"HoD recommendation: {record['head_recommendation']} "
            f"by {record['head_recommended_by'] or '-'} "
            f"on {record['head_recommendation_date'] or '-'}",
            f"SMT decision: {record['smt_decision']} "
            f"by {record['smt_decided_by'] or '-'} "
            f"on {record['smt_decision_date'] or '-'}",
            f"Appeal status: {record['appeal_status']}",
            f"Reviewer notes: {record['reviewer_notes'] or '-'}",
        ]

        self.show_text_window(
            f"Permit application #{record['id']}",
            "\n".join(details)
        )

    def build_issued_permits_tab(self):
        self.issued_permits_tab.columnconfigure(0, weight=1)
        self.issued_permits_tab.rowconfigure(0, weight=1)

        table_frame = ttk.LabelFrame(
            self.issued_permits_tab,
            text="Issued permits",
            padding=8
        )
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = (
            "ID",
            "Permit No",
            "Holder",
            "Kind",
            "Scope",
            "Reg 1",
            "Reg 2",
            "Issued",
            "Expiry",
            "Status"
        )

        self.issued_permits_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=22
        )

        for col in columns:
            self.issued_permits_tree.heading(col, text=col)
            self.issued_permits_tree.column(col, width=120, anchor="center")

        self.issued_permits_tree.column("Holder", width=170, anchor="w")
        self.issued_permits_tree.column("Permit No", width=150, anchor="w")
        self.issued_permits_tree.column("Scope", width=150, anchor="w")
        self.issued_permits_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.issued_permits_tree.yview
        )
        self.issued_permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        controls = ttk.Frame(table_frame)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        for i in range(11):
            if i in {1, 3, 5}:
                controls.columnconfigure(i, weight=1)
            else:
                controls.columnconfigure(i, weight=0)

        ttk.Label(controls, text="Status").grid(row=0, column=0, sticky="w")
        self.issued_status_var = tk.StringVar(value="Collected")
        ttk.Combobox(
            controls,
            textvariable=self.issued_status_var,
            values=ISSUED_PERMIT_STATUSES,
            state="readonly",
            width=22
        ).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="Notes").grid(row=0, column=2, sticky="w")
        self.issued_notes_var = tk.StringVar()
        ttk.Entry(
            controls,
            textvariable=self.issued_notes_var
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="Replacement fee").grid(
            row=0, column=4, sticky="w"
        )
        self.replacement_fee_var = tk.StringVar(value="0")
        ttk.Entry(
            controls,
            textvariable=self.replacement_fee_var,
            width=8
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        ttk.Button(
            controls,
            text="Update selected",
            command=self.update_selected_issued_permit
        ).grid(row=0, column=6, sticky="ew")

        ttk.Button(
            controls,
            text="View selected",
            command=self.show_selected_issued_permit
        ).grid(row=0, column=7, sticky="ew", padx=(8, 12))

        ttk.Label(controls, text="New reg 1").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        self.new_reg1_var = tk.StringVar()
        ttk.Entry(
            controls,
            textvariable=self.new_reg1_var
        ).grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=(8, 0))

        ttk.Label(controls, text="New reg 2").grid(
            row=1, column=2, sticky="w", pady=(8, 0)
        )
        self.new_reg2_var = tk.StringVar()
        ttk.Entry(
            controls,
            textvariable=self.new_reg2_var
        ).grid(row=1, column=3, sticky="ew", padx=(8, 12), pady=(8, 0))

        ttk.Button(
            controls,
            text="Update vehicle details",
            command=self.update_selected_issued_permit_regs
        ).grid(
            row=1,
            column=4,
            columnspan=2,
            sticky="ew",
            pady=(8, 0)
        )

        ttk.Button(
            controls,
            text="Refresh",
            command=self.refresh_issued_permits
        ).grid(row=1, column=6, sticky="ew", pady=(8, 0))

    def update_selected_issued_permit(self):
        try:
            permit_id = self.selected_tree_id(self.issued_permits_tree)

            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select an issued permit first."
                )
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
                messagebox.showwarning(
                    "No selection",
                    "Please select an issued permit first."
                )
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
            messagebox.showwarning(
                "No selection",
                "Please select an issued permit first."
            )
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

        self.show_text_window(
            f"Issued permit #{record['id']}",
            "\n".join(details)
        )