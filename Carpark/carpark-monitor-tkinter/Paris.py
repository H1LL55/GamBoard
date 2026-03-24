# tkinter is Python's built-in GUI library.
# We rename tkinter to "tk" because it is shorter to type and is the common convention.
import tkinter as tk

# ttk gives us the themed widgets such as nicer buttons, labels, comboboxes and treeviews.
# messagebox is used for popup messages like warnings, errors and success messages.
from tkinter import ttk, messagebox


# These values and helper functions are imported from shared_db.py.
# They are being reused here so this file does not need to hard-code them again.
from shared_db import (
    COLLECTION_LOCATIONS,        # List of valid permit collection locations
    ISSUED_PERMIT_STATUSES,      # Status options for permits that have already been issued
    PERMIT_APP_STATUSES,         # Status options for permit applications under review
    PERMIT_KIND_OPTIONS,         # Types of permit that can be issued
    as_yes_no,                   # Helper function that converts True/False into Yes/No
    default_expiry_str,          # Helper function that returns a default expiry date as text
    ensure_date,                 # Helper function that validates a date entered by the user
)

# This import is duplicated in your original code.
# It does not change the behaviour, but it is unnecessary because the same names
# have already been imported above.
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
    #
    # This class is a "mixin", which means it is designed to be added into another class
    # rather than used by itself.
    #
    # It assumes the main program already has things such as:
    # - self.db                      -> the database object
    # - self.permits_tab             -> the permit applications tab
    # - self.issued_permits_tab      -> the issued permits tab
    # - self.selected_tree_id(...)   -> helper method to get selected row ID from a table
    # - self.require(...)            -> helper method to make sure a field is not blank
    # - self.refresh_all()           -> helper method to reload all tables
    # - self.refresh_permits()       -> helper method to reload permit applications
    # - self.refresh_issued_permits()-> helper method to reload issued permits

    def build_permits_tab(self):
        # This method builds the whole "permits" tab in the GUI.
        # It creates:
        # 1. A table showing permit applications
        # 2. A review area for changing application status
        # 3. An issue area for creating an issued permit from an approved application

        # Make column 0 in the permits tab expand when the window gets bigger.
        self.permits_tab.columnconfigure(0, weight=1)

        # Make row 0 expand too, so the main content stretches with the window.
        self.permits_tab.rowconfigure(0, weight=1)

        # Create a bordered frame with a title to hold the application table and controls.
        table_frame = ttk.LabelFrame(
            self.permits_tab,
            text="Applications and review",
            padding=8
        )

        # Put the frame into the permits tab.
        # sticky="nsew" means it stretches in all directions.
        table_frame.grid(row=0, column=0, sticky="nsew")

        # Make the inside of the frame expandable too.
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # These are the column headings that will appear in the Treeview table.
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

        # Create the Treeview widget.
        # This is the table that shows all permit applications.
        self.permits_tree = ttk.Treeview(
            table_frame,
            columns=permit_columns,  # Use the headings listed above
            show="headings",         # Only show the headings, not the hidden tree column
            height=20                # Show roughly 20 rows high
        )

        # Loop through each column name and set up the heading text
        # and default width/alignment.
        for col in permit_columns:
            self.permits_tree.heading(col, text=col)
            self.permits_tree.column(col, width=110, anchor="center")

        # Some columns need more space and look better left-aligned.
        self.permits_tree.column("Name", width=160, anchor="w")
        self.permits_tree.column("Email", width=190, anchor="w")
        self.permits_tree.column("Car park", width=220, anchor="w")

        # Place the table into the frame.
        self.permits_tree.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar for the permit applications table.
        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.permits_tree.yview
        )

        # Connect the table to the scrollbar so they move together.
        self.permits_tree.configure(yscrollcommand=yscroll.set)

        # Put the scrollbar beside the table.
        yscroll.grid(row=0, column=1, sticky="ns")

        # Create a frame underneath the table for the review controls.
        # This section lets the user update the application status,
        # enter reviewer info, add notes, and view details.
        review = ttk.Frame(table_frame)
        review.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # Configure the columns in the review frame.
        # The columns in {3, 5, 6} are made stretchable so text fields
        # and some buttons can grow when the window size changes.
        for i in range(9):
            if i in {3, 5, 6}:
                review.columnconfigure(i, weight=1)
            else:
                review.columnconfigure(i, weight=0)

        # Label for the status dropdown.
        ttk.Label(review, text="Review status").grid(
            row=0, column=0, sticky="w"
        )

        # StringVar stores the selected application status in memory.
        # It starts with "Awaiting SMT Approval" as the default value.
        self.permit_status_var = tk.StringVar(value="Awaiting SMT Approval")

        # Combobox lets the user choose one of the valid application statuses.
        ttk.Combobox(
            review,
            textvariable=self.permit_status_var,
            values=PERMIT_APP_STATUSES,
            state="readonly",   # User can only select from the list, not type their own value
            width=22
        ).grid(row=0, column=1, sticky="w", padx=(8, 12))

        # Label for the reviewer name input.
        ttk.Label(review, text="Reviewer").grid(row=0, column=2, sticky="w")

        # This stores the reviewer name entered into the entry box.
        self.permit_reviewer_var = tk.StringVar()

        # Entry box for the reviewer name.
        ttk.Entry(
            review,
            textvariable=self.permit_reviewer_var,
            width=16
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        # Label for review notes.
        ttk.Label(review, text="Notes").grid(row=0, column=4, sticky="w")

        # StringVar to hold any review notes typed by the staff member.
        self.permit_review_notes = tk.StringVar()

        # Entry box for review notes.
        ttk.Entry(
            review,
            textvariable=self.permit_review_notes
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        # Button to save the chosen review status for whichever application is selected.
        ttk.Button(
            review,
            text="Update selected",
            command=self.update_selected_permit_status
        ).grid(row=0, column=6, sticky="ew")

        # Button to open a detailed view of the selected application.
        ttk.Button(
            review,
            text="View selected",
            command=self.show_selected_permit_details
        ).grid(row=0, column=7, sticky="ew", padx=(8, 12))

        # Button to reload the permit application table from the database.
        ttk.Button(
            review,
            text="Refresh",
            command=self.refresh_permits
        ).grid(row=0, column=8, sticky="ew")

        # Create another frame under the review controls.
        # This section is for turning an approved application into a real issued permit.
        issue_frame = ttk.Frame(table_frame)
        issue_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # Configure layout for the issue controls.
        for i in range(8):
            if i in {1, 3, 5}:
                issue_frame.columnconfigure(i, weight=1)
            else:
                issue_frame.columnconfigure(i, weight=0)

        # Label for permit kind.
        ttk.Label(issue_frame, text="Issue permit kind").grid(
            row=0, column=0, sticky="w"
        )

        # Store the permit kind to issue.
        # Default is "Standard".
        self.issue_permit_kind_var = tk.StringVar(value="Standard")

        # Dropdown for selecting the permit kind.
        ttk.Combobox(
            issue_frame,
            textvariable=self.issue_permit_kind_var,
            values=PERMIT_KIND_OPTIONS,
            state="readonly",
            width=18
        ).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        # Label for permit scope.
        ttk.Label(issue_frame, text="Scope").grid(row=0, column=2, sticky="w")

        # This holds the scope entered by the user.
        # Scope might mean where the permit is valid, for example a campus or area.
        self.issue_scope_var = tk.StringVar()

        # Entry box for scope.
        ttk.Entry(
            issue_frame,
            textvariable=self.issue_scope_var
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        # Label for expiry date.
        ttk.Label(issue_frame, text="Expiry").grid(row=0, column=4, sticky="w")

        # Default expiry is filled in automatically using a helper function.
        self.issue_expiry_var = tk.StringVar(value=default_expiry_str())

        # Entry box for expiry date.
        ttk.Entry(
            issue_frame,
            textvariable=self.issue_expiry_var,
            width=14
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        # Store the selected collection location.
        # A default collection location is already chosen when the screen loads.
        self.issue_collection_var = tk.StringVar(
            value="Old Sessions House reception"
        )

        # Dropdown for collection location.
        ttk.Combobox(
            issue_frame,
            textvariable=self.issue_collection_var,
            values=COLLECTION_LOCATIONS,
            state="readonly",
            width=24
        ).grid(row=0, column=6, sticky="ew", padx=(0, 12))

        # Button that creates an issued permit from the selected approved application.
        ttk.Button(
            issue_frame,
            text="Issue from selected approved application",
            command=self.issue_selected_permit
        ).grid(row=0, column=7, sticky="ew")

    def update_selected_permit_status(self):
        # This method updates the review status of the currently selected permit application.
        # Example: changing it from "Awaiting SMT Approval" to "Approved".

        try:
            # Get the ID of the currently selected row from the permit applications table.
            permit_id = self.selected_tree_id(self.permits_tree)

            # If nothing is selected, show a warning and stop the method.
            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select a permit application first."
                )
                return

            # Make sure the reviewer name has been entered.
            # self.require(...) likely raises an error if the field is blank.
            reviewer = self.require(
                self.permit_reviewer_var.get(),
                "Reviewer"
            )

            # Update the selected permit application in the database.
            # It saves:
            # - the application ID
            # - the chosen status
            # - the reviewer name
            # - any notes typed into the notes field
            self.db.update_permit_status(
                permit_id,
                self.permit_status_var.get(),
                reviewer,
                self.permit_review_notes.get().strip()
            )

            # Refresh all tables so the updated data appears on screen immediately.
            self.refresh_all()

            # Tell the user the action worked.
            messagebox.showinfo("Updated", "Permit status updated.")

        except Exception as exc:
            # If anything goes wrong, show the error in a popup.
            messagebox.showerror("Could not update", str(exc))

    def issue_selected_permit(self):
        # This method turns a selected application into an issued permit.
        # It is likely meant to be used once an application has been approved.

        try:
            # Get the selected application ID from the applications table.
            permit_id = self.selected_tree_id(self.permits_tree)

            # If no row is selected, warn the user and stop.
            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select an approved application first."
                )
                return

            # Validate the expiry date entered in the issue section.
            # allow_blank=False means the expiry date must be filled in.
            expiry = ensure_date(
                self.issue_expiry_var.get(),
                "Issue expiry",
                allow_blank=False
            )

            # Call the database method that creates the issued permit
            # using the selected application as the source.
            self.db.issue_permit_from_application(
                permit_id,
                self.issue_permit_kind_var.get().strip(),   # Permit type, e.g. Standard
                self.issue_scope_var.get().strip(),         # Scope entered by staff
                expiry,                                     # Validated expiry date
                self.issue_collection_var.get().strip(),    # Collection location
                self.permit_review_notes.get().strip(),     # Optional notes
            )

            # Reload everything so the UI reflects the new issued permit.
            self.refresh_all()

            # Let the user know the permit was created successfully.
            messagebox.showinfo(
                "Issued",
                "Permit created and marked ready for collection."
            )

        except Exception as exc:
            # Show any error that happens during issue creation.
            messagebox.showerror("Could not issue", str(exc))

    def show_text_window(self, title, text):
        # This is a reusable helper method.
        # It opens a new popup window and displays a large block of text inside it.
        # It is used for showing full permit details.

        # Create a new top-level window.
        # This is a separate popup window, not a whole new app.
        top = tk.Toplevel(self)

        # Set the title shown in the popup's title bar.
        top.title(title)

        # Set the size of the popup window.
        top.geometry("760x640")

        # Make this popup behave as a child of the main window.
        # It stays linked to the main application.
        top.transient(self)

        # Create a frame inside the popup to give padding around the content.
        frame = ttk.Frame(top, padding=12)
        frame.pack(fill="both", expand=True)

        # Create a multi-line text box.
        # wrap="word" means lines wrap at whole words rather than splitting words.
        # Consolas is used for a neat, readable fixed-width font.
        text_box = tk.Text(frame, wrap="word", font=("Consolas", 10))
        text_box.pack(side="left", fill="both", expand=True)

        # Add a vertical scrollbar to the text box.
        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=text_box.yview
        )
        scroll.pack(side="right", fill="y")

        # Link the text box and the scrollbar together.
        text_box.configure(yscrollcommand=scroll.set)

        # Insert the provided text into the text box starting at line 1, character 0.
        text_box.insert("1.0", text)

        # Make the text box read-only so the user cannot edit the details.
        text_box.configure(state="disabled")

    def show_selected_permit_details(self):
        # This method shows full details of the currently selected permit application
        # in a popup text window.

        # Get the selected permit application ID from the applications table.
        permit_id = self.selected_tree_id(self.permits_tree)

        # If no application is selected, warn the user and stop.
        if not permit_id:
            messagebox.showwarning(
                "No selection",
                "Please select an application first."
            )
            return

        # Ask the database for the full record of that application.
        record = self.db.get_permit_application(permit_id)

        # Build a list of text lines that describe the application in detail.
        # f-strings are used so values from the database record can be inserted into the text.
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

        # Join the list into one block of text with a line break between each item,
        # then show it in the popup window.
        self.show_text_window(
            f"Permit application #{record['id']}",
            "\n".join(details)
        )

    def build_issued_permits_tab(self):
        # This method builds the second main tab:
        # the tab that shows permits that have already been issued.

        # Make the tab stretch with the window.
        self.issued_permits_tab.columnconfigure(0, weight=1)
        self.issued_permits_tab.rowconfigure(0, weight=1)

        # Create the outer frame with a title.
        table_frame = ttk.LabelFrame(
            self.issued_permits_tab,
            text="Issued permits",
            padding=8
        )
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Define the columns for the issued permits table.
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

        # Create the Treeview table for issued permits.
        self.issued_permits_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=22
        )

        # Set up each column heading and default appearance.
        for col in columns:
            self.issued_permits_tree.heading(col, text=col)
            self.issued_permits_tree.column(col, width=120, anchor="center")

        # Make some columns wider and left-aligned for readability.
        self.issued_permits_tree.column("Holder", width=170, anchor="w")
        self.issued_permits_tree.column("Permit No", width=150, anchor="w")
        self.issued_permits_tree.column("Scope", width=150, anchor="w")

        # Place the table on screen.
        self.issued_permits_tree.grid(row=0, column=0, sticky="nsew")

        # Create the vertical scrollbar for the issued permits table.
        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.issued_permits_tree.yview
        )

        # Link the scrollbar to the table.
        self.issued_permits_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        # Create a controls section under the table.
        # This area allows updates to status, notes, replacement fee and vehicle details.
        controls = ttk.Frame(table_frame)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # Configure column expansion for the controls area.
        for i in range(11):
            if i in {1, 3, 5}:
                controls.columnconfigure(i, weight=1)
            else:
                controls.columnconfigure(i, weight=0)

        # Label for status dropdown.
        ttk.Label(controls, text="Status").grid(row=0, column=0, sticky="w")

        # Store the selected issued-permit status.
        # Default starts as "Collected".
        self.issued_status_var = tk.StringVar(value="Collected")

        # Dropdown of valid issued permit statuses.
        ttk.Combobox(
            controls,
            textvariable=self.issued_status_var,
            values=ISSUED_PERMIT_STATUSES,
            state="readonly",
            width=22
        ).grid(row=0, column=1, sticky="ew", padx=(8, 12))

        # Label for notes field.
        ttk.Label(controls, text="Notes").grid(row=0, column=2, sticky="w")

        # Holds notes about the issued permit.
        self.issued_notes_var = tk.StringVar()

        # Entry for notes.
        ttk.Entry(
            controls,
            textvariable=self.issued_notes_var
        ).grid(row=0, column=3, sticky="ew", padx=(8, 12))

        # Label for replacement fee.
        ttk.Label(controls, text="Replacement fee").grid(
            row=0, column=4, sticky="w"
        )

        # Stores the replacement fee as text first.
        # It starts at "0".
        self.replacement_fee_var = tk.StringVar(value="0")

        # Entry for replacement fee.
        ttk.Entry(
            controls,
            textvariable=self.replacement_fee_var,
            width=8
        ).grid(row=0, column=5, sticky="ew", padx=(8, 12))

        # Button to update the selected issued permit record.
        ttk.Button(
            controls,
            text="Update selected",
            command=self.update_selected_issued_permit
        ).grid(row=0, column=6, sticky="ew")

        # Button to view the selected issued permit in detail.
        ttk.Button(
            controls,
            text="View selected",
            command=self.show_selected_issued_permit
        ).grid(row=0, column=7, sticky="ew", padx=(8, 12))

        # Label for new primary vehicle registration.
        ttk.Label(controls, text="New reg 1").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )

        # Variable holding the new primary registration.
        self.new_reg1_var = tk.StringVar()

        # Entry for the new primary registration.
        ttk.Entry(
            controls,
            textvariable=self.new_reg1_var
        ).grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=(8, 0))

        # Label for new secondary vehicle registration.
        ttk.Label(controls, text="New reg 2").grid(
            row=1, column=2, sticky="w", pady=(8, 0)
        )

        # Variable holding the new secondary registration.
        self.new_reg2_var = tk.StringVar()

        # Entry for the new secondary registration.
        ttk.Entry(
            controls,
            textvariable=self.new_reg2_var
        ).grid(row=1, column=3, sticky="ew", padx=(8, 12), pady=(8, 0))

        # Button to update the vehicle registration(s) for the selected issued permit.
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

        # Button to reload the issued permits table.
        ttk.Button(
            controls,
            text="Refresh",
            command=self.refresh_issued_permits
        ).grid(row=1, column=6, sticky="ew", pady=(8, 0))

    def update_selected_issued_permit(self):
        # This method updates the selected issued permit record,
        # such as its status, notes and replacement fee.

        try:
            # Get the selected issued permit ID from the table.
            permit_id = self.selected_tree_id(self.issued_permits_tree)

            # If nothing is selected, warn the user and stop.
            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select an issued permit first."
                )
                return

            # Update the issued permit in the database.
            # The replacement fee is converted from text into a float.
            # If the box is left blank, it becomes "0".
            self.db.update_issued_permit(
                permit_id,
                self.issued_status_var.get(),
                self.issued_notes_var.get().strip(),
                float(self.replacement_fee_var.get().strip() or "0"),
            )

            # Refresh all GUI data after the update.
            self.refresh_all()

            # Show success message.
            messagebox.showinfo("Updated", "Issued permit updated.")

        except Exception as exc:
            # Show any error that occurs.
            messagebox.showerror("Could not update", str(exc))

    def update_selected_issued_permit_regs(self):
        # This method updates the vehicle registration details
        # for the selected issued permit.

        try:
            # Get the selected issued permit ID.
            permit_id = self.selected_tree_id(self.issued_permits_tree)

            # If no permit is selected, warn the user and stop.
            if not permit_id:
                messagebox.showwarning(
                    "No selection",
                    "Please select an issued permit first."
                )
                return

            # Update the primary and secondary registration in the database.
            # The first registration is required.
            # The second one can be blank.
            self.db.update_issued_permit_regs(
                permit_id,
                self.require(self.new_reg1_var.get(), "New reg 1"),
                self.new_reg2_var.get().strip(),
            )

            # Refresh the UI to show the new registration data.
            self.refresh_all()

            # Clear the entry boxes after a successful update.
            self.new_reg1_var.set("")
            self.new_reg2_var.set("")

            # Show success message.
            messagebox.showinfo("Updated", "Permit vehicle details updated.")

        except Exception as exc:
            # Show any error message if something fails.
            messagebox.showerror("Could not update", str(exc))

    def show_selected_issued_permit(self):
        # This method displays all details for the selected issued permit
        # in a popup window.

        # Get the selected issued permit ID.
        permit_id = self.selected_tree_id(self.issued_permits_tree)

        # If nothing is selected, warn the user and stop.
        if not permit_id:
            messagebox.showwarning(
                "No selection",
                "Please select an issued permit first."
            )
            return

        # Get the full issued permit record from the database.
        record = self.db.get_issued_permit(permit_id)

        # Build a readable list of lines showing all important details.
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

        # Show the details in the reusable text popup window.
        self.show_text_window(
            f"Issued permit #{record['id']}",
            "\n".join(details)
        )