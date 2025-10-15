import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT username FROM users")
data = cursor.fetchall()

for user in data:
    print("Username:", user[0])

conn.close()
