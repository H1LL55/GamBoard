# Run this once from the terminal to create the first admin account.
# After that, use the Manage Users tab inside the app.

from shared_db import DB_PATH, DatabaseManager

db = DatabaseManager(DB_PATH)

print("=== CCCU Car Park Monitor - First Time Setup ===")
username = input("Choose an admin username: ").strip()
password = input("Choose a password (min 6 characters): ")

if len(password) < 6:
    print("Password too short. Please try again.")
else:
    db.add_user(username, password)
    print(f"\nAccount '{username}' created. You can now log in to the app.")