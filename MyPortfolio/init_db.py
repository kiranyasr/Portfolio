# ------------------- init_db.py -------------------
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop existing tables if they exist
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS about")
c.execute("DROP TABLE IF EXISTS projects")
c.execute("DROP TABLE IF EXISTS skills")

# Users table
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

# About table
c.execute('''
CREATE TABLE about (
    id INTEGER PRIMARY KEY,
    bio TEXT,
    name TEXT,
    dob TEXT,
    address TEXT,
    zip_code TEXT,
    email TEXT,
    phone TEXT,
    projects_completed INTEGER,
    photo TEXT
)
''')

# ❌ Skills table without percentage column
c.execute('''
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image TEXT
)
''')

# Projects table
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

# Insert default About info (editable later)
c.execute('''
INSERT INTO about (
    id, bio, name, dob, address, zip_code, email, phone, projects_completed, photo
) VALUES (
    1,
    'This is your editable bio.',
    'Your Name',
    'DD-MM-YYYY',
    'Your address here',
    '000000',
    'your@email.com',
    '+91 XXXXXXXXXX',
    0,
    'default.png'
)
''')

conn.commit()
conn.close()
print("✅ Database initialized successfully.")
