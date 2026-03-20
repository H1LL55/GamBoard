# CCCU Car Park Monitor (Tkinter)

This is a desktop prototype of the car park monitor system built in Python with Tkinter and SQLite.

## What it does

- Stores permit applications for staff and students
- Stores visitor bookings
- Stores temporary permits
- Stores event / contractor / guest reservations
- Lets patrol staff check a vehicle registration against current records
- Logs penalty notices and records whether they were sent to Workflow Dynamics
- Seeds the database with car park data based on the uploaded spreadsheet

## Files

- `carpark_monitor_tkinter.py` - main application
- `carpark_monitor.db` - SQLite database (created automatically the first time you run the app)

## How to run

1. Make sure Python 3 is installed
2. Open a terminal / command prompt in this folder
3. Run:

```bash
python carpark_monitor_tkinter.py
```

## Data storage

All data is stored locally in an SQLite database file called `carpark_monitor.db` in the same folder as the script.

## Notes

- Date format is `YYYY-MM-DD`
- The app is designed as a practical desktop prototype / MVP
- Permit applications are saved as `Pending` first, then can be reviewed to `Approved` or `Declined`
- The permit checker looks for:
  - approved standard permits
  - active temporary permits
  - visitor bookings for the selected date
  - active reservations linked to that vehicle registration

## Suggested next upgrades

- Add login roles (helpdesk / security / admin)
- Add edit and delete buttons
- Add CSV export for reports
- Add search and filter boxes on each tab
- Add printable permit and visitor pass views
- Add email notifications for approved / declined applications
- Convert the SQLite database to MySQL or PostgreSQL later if you want a shared multi-user version
