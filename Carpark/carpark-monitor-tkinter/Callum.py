import tkinter as tk                                                    # Import tkinter for GUI components
from tkinter import ttk, messagebox                                      # Import themed widgets and popup dialogs

from shared_db import DB_PATH, DatabaseManager                         # Import database path and manager from shared module


class CallumMixin:                                                      # Mixin class to be combined with the main app class
    # Callum - work on this file
    # Login screen, dashboard startup, header and notebook tabs

    def build_login_screen(self):                                       # Builds the initial login UI before dashboard is shown
        self.login_frame = ttk.Frame(self, padding=24)                  # Creates outer frame with padding to hold all login widgets
        self.login_frame.grid(row=0, column=0, sticky="nsew")           # Places frame filling the whole window
        self.login_frame.columnconfigure(0, weight=1)                   # Allows the column to stretch horizontally

        card = ttk.LabelFrame(self.login_frame, text="Admin login", padding=18)    # Creates a bordered card with a title label
        card.grid(row=0, column=0, sticky="n", pady=(16, 0))            # Places card at top-centre with a small top margin
        card.columnconfigure(1, weight=1)                               # Allows the right column (inputs) to stretch

        ttk.Label(
            card,
            text="CCCU Car Park Monitor",
            font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))  # App title spanning both columns, bold and large

        ttk.Label(
            card,
            text="Please sign in before accessing the admin dashboard.",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14)) # Subtitle instruction text below the title

        ttk.Label(card, text="Username").grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )                                                               # "Username" label in the left column
        username_entry = ttk.Entry(
            card,
            textvariable=self.login_username_var,                       # Binds input to a tracked variable for easy reading
            width=28
        )
        username_entry.grid(row=2, column=1, sticky="ew", pady=4)      # Username text input in the right column

        ttk.Label(card, text="Password").grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )                                                               # "Password" label in the left column
        password_entry = ttk.Entry(
            card,
            textvariable=self.login_password_var,                       # Binds input to a tracked variable for easy reading
            show="*",                                                   # Masks characters so password is hidden
            width=28
        )
        password_entry.grid(row=3, column=1, sticky="ew", pady=4)      # Password text input in the right column

        ttk.Button(
            card,
            text="Login",
            command=self.try_login                                      # Calls try_login when button is clicked
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))  # Login button spanning both columns

        self.bind("<Return>", self.try_login)                           # Also triggers login when Enter key is pressed
        username_entry.focus_set()                                      # Automatically focuses the username field on load

    def try_login(self, event=None):
        username = self.login_username_var.get().strip()
        password = self.login_password_var.get()

        # Open the database to check the login
        from shared_db import DB_PATH, DatabaseManager
        temp_db = DatabaseManager(DB_PATH)

        # If no users exist yet, tell them to run setup_admin.py first
        if not temp_db.list_users():
            messagebox.showwarning(
                "No accounts",
                "No admin accounts exist yet.\n\nRun setup_admin.py first to create the first account."
            )
            return

        if temp_db.check_password(username, password):
            self.unbind("<Return>")
            self.current_user = username  
            if self.login_frame is not None:
                self.login_frame.destroy()
            self.show_dashboard()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            self.login_password_var.set("")

    def show_dashboard(self):                                           # Sets up and displays the full admin dashboard after login
        self.title("CCCU Car Park Monitor - Admin Dashboard")           # Updates the window title bar
        self.state('zoomed')                                            # Maximizes the window to full screen
        self.minsize(1320, 820)                                         # Prevents the window being resized smaller than this
        self.rowconfigure(1, weight=1)                                  # Allows the main content row to expand vertically

        self.db = DatabaseManager(DB_PATH)                              # Opens a connection to the database
        self.car_park_choices = self.db.car_park_options()              # Loads car park names/IDs for use in dropdowns

        self.build_header()                                             # Renders the top title bar
        self.build_notebook()                                           # Renders the tabbed interface and all tab contents
        self.refresh_all()                                              # Loads initial data into all tabs
        self.start_auto_refresh()                                       # Starts a timer to periodically refresh data

    def build_header(self):                                             # Builds the top bar shown above the tabs on the dashboard
        header = ttk.Frame(self, padding=(16, 12))                      # Creates a frame with horizontal and vertical padding
        header.grid(row=0, column=0, sticky="ew")                      # Places header spanning the full width at the top
        header.columnconfigure(0, weight=1)  
        ttk.Button(
        header,
        text="Logout",
        command=self.logout
    ).grid(row=0, column=1, sticky="e", padx=(12, 0))                           # Allows the header content to stretch horizontally

        ttk.Label(
            header,
            text="CCCU Car Park Monitor",
            font=("Segoe UI", 20, "bold")
        ).grid(row=0, column=0, sticky="w")                            # Large bold app title aligned to the left

        ttk.Label(
            header,
            text=(
                "Admin dashboard for reviewing permit applications, issuing permits, "
                "managing visitors, reservations, patrol checks and penalty notices."
            ),
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))               # Smaller subtitle describing the dashboard's purpose

    def build_notebook(self):                                           # Creates the tabbed notebook interface and populates each tab
        self.notebook = ttk.Notebook(self)                              # Creates the tab container widget
        self.notebook.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )                                                               # Places notebook filling the main content area with margins

        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)      # Frame for the overview/summary tab
        self.permits_tab = ttk.Frame(self.notebook, padding=12)        # Frame for reviewing pending permit applications
        self.issued_permits_tab = ttk.Frame(self.notebook, padding=12) # Frame for viewing active and historical permits
        self.checker_tab = ttk.Frame(self.notebook, padding=12)        # Frame for the patrol permit checking tool
        self.penalties_tab = ttk.Frame(self.notebook, padding=12)      # Frame for issuing and viewing penalty notices
        if self.current_user == "admin":
            self.users_tab = ttk.Frame(self.notebook, padding=12)
            self.notebook.add(self.users_tab, text="Manage Users")
            self.build_users_tab()

        self.notebook.add(self.dashboard_tab, text="Dashboard")                     # Registers the Dashboard tab
        self.notebook.add(self.permits_tab, text="Permit Applications")             # Registers the Permit Applications tab
        self.notebook.add(self.issued_permits_tab, text="Issued Permits")           # Registers the Issued Permits tab
        self.notebook.add(self.checker_tab, text="Permit Check")                    # Registers the Permit Check tab
        self.notebook.add(self.penalties_tab, text="Penalty Notices")               # Registers the Penalty Notices tab

        self.build_dashboard_tab()      # adds the Dashboard tab with its widgets
        self.build_permits_tab()        # adds the Permit Applications tab with its widgets
        self.build_issued_permits_tab() # adds the Issued Permits tab with its widgets
        self.build_checker_tab()        # adds the Permit Check tab with its widgets
        self.build_penalties_tab()      # adds the Penalty Notices tab with its widgets