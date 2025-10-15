import sqlite3

# Database connection
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create a table (if not already present)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert some data (if desired)
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("zahed", "abcd"))
cursor.execute("INSERT INTO users (username,password) VALUES(?,?)",("zawad","xyz"))


# Save changes
conn.commit()

conn.close()
print("✅ The users table has been created and data has been added.")
