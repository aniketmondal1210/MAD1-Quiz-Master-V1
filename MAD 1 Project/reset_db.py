import os
import sqlite3

# Delete the existing database file
db_file = 'quiz_master.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Deleted existing database: {db_file}")

# Create a new empty database
conn = sqlite3.connect(db_file)
conn.close()
print(f"Created new empty database: {db_file}")

print("Database reset complete. Now run 'python run.py' to initialize the application.")
