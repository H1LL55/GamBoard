import tkinter as tk
from tkinter import ttk

class KrisMixin:
    # Kris - work on this file
    # Dashboard tab and all refresh functions.

    def build_dashboard_tab(self):
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)

        self.kpi_frame = ttk.Frame(self.dashboard_tab)
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        for i in range(5):
            self.kpi_frame.columnconfigure(i, weight=1)

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

        for i, item in enumerate(kpi_titles):
            key = item[0]
            title = item[1]

            card = ttk.LabelFrame(self.kpi_frame, text=title, padding=12)
            card.grid(
                row=i // 5,
                column=i % 5,
                sticky="nsew",
                padx=6,
                pady=6
            )

            label = ttk.Label(card, text="0", font=("Segoe UI", 18, "bold"))
            label.pack(anchor="center", pady=8)

            self.kpi_labels[key] = label

        lower = ttk.Panedwindow(self.dashboard_tab, orient=tk.HORIZONTAL)
        lower.grid(row=1, column=0, sticky="nsew")

        carparks_frame = ttk.LabelFrame(
            lower,
            text="Car park overview",
            padding=8
        )
        notes_frame = ttk.LabelFrame(lower, text=" ", padding=10)

        lower.add(carparks_frame, weight=3)
        lower.add(notes_frame, weight=2)

        carparks_frame.columnconfigure(0, weight=1)
        carparks_frame.rowconfigure(0, weight=1)

        columns = (
            "Campus",
            "Name",
            "Standard",
            "Visitor",
            "Electric",
            "Disabled",
            "Total"
        )

        self.carparks_tree = ttk.Treeview(
            carparks_frame,
            columns=columns,
            show="headings",
            height=16
        )

        for col in columns:
            self.carparks_tree.heading(col, text=col)
            self.carparks_tree.column(col, width=120, anchor="center")

        self.carparks_tree.column("Name", width=270, anchor="w")
        self.carparks_tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(
            carparks_frame,
            orient="vertical",
            command=self.carparks_tree.yview
        )
        self.carparks_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        notes_text = (
            "• Applicants now submit new permit requests through the separate "
            "application form file.\n\n"
            "• This dashboard is staff/admin side only.\n\n"
            "• Permit applications saved in the other file appear here because "
            "both files use the same SQLite database.\n\n"
            "• The dashboard auto-refreshes so review staff can see new "
            "applications coming in without reopening the whole system.\n\n"
            "• Visitors, reservations, temporary permits, patrol checks and "
            "penalty notices need to be accepted here."
        )

        ttk.Label(
            notes_frame,
            text=notes_text,
            justify="left",
            wraplength=430
        ).pack(fill="both", expand=True)

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
        self.replace_tree_data(
            self.permits_tree,
            self.db.list_permit_applications()
        )

    def refresh_issued_permits(self):
        self.replace_tree_data(
            self.issued_permits_tree,
            self.db.list_issued_permits()
        )

    def refresh_visitors(self):
        self.replace_tree_data(
            self.visitors_tree,
            self.db.list_visitor_bookings()
        )

    def refresh_reservations(self):
        self.replace_tree_data(
            self.reservations_tree,
            self.db.list_reservations()
        )

    def refresh_temp_permits(self):
        self.replace_tree_data(
            self.temp_tree,
            self.db.list_temporary_permits()
        )

    def refresh_penalties(self):
        self.replace_tree_data(
            self.penalties_tree,
            self.db.list_penalties()
        )

    def start_auto_refresh(self):
        self.after(10000, self.auto_refresh_tick)

    def auto_refresh_tick(self):
        try:
            self.refresh_dashboard()
            self.refresh_permits()
            self.refresh_issued_permits()
        finally:
            self.after(10000, self.auto_refresh_tick)