import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop tables if they exist (for clean start)
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS about")
c.execute("DROP TABLE IF EXISTS projects")

# Create users table
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# Create about table
c.execute('''
CREATE TABLE about (
    id INTEGER PRIMARY KEY,
    bio TEXT
)
''')

# Create projects table with all required columns
c.execute('''
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tech_stack TEXT,
    github TEXT,
    demo TEXT,
    image TEXT,
    outcome TEXT,
    tools TEXT,
    use_case TEXT
)
''')

# Insert default admin user
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))

# Insert default about bio
c.execute("INSERT INTO about (id, bio) VALUES (1, 'This is your editable bio.')")

conn.commit()
conn.close()

print("✅ Database initialized successfully.")
