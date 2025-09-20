# ------------------- init_db.py -------------------
import sqlite3
import os

# Get base directory of this file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database path
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# Drop existing tables for a clean slate
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS about")
c.execute("DROP TABLE IF EXISTS projects")
c.execute("DROP TABLE IF EXISTS skills")
c.execute("DROP TABLE IF EXISTS experience")
c.execute("DROP TABLE IF EXISTS certificates")
c.execute("DROP TABLE IF EXISTS technical_platforms")
c.execute("DROP TABLE IF EXISTS home_content")

# --- Create All Tables ---

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
    id INTEGER PRIMARY KEY, bio TEXT, name TEXT, dob TEXT, address TEXT, 
    zip_code TEXT, email TEXT, phone TEXT, projects_completed INTEGER, photo TEXT
)
''')

# Skills table
c.execute('''
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, image TEXT
)
''')

# Projects table
c.execute('''
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, tech_stack TEXT,
    github TEXT, demo TEXT, image TEXT, outcome TEXT, tools TEXT, use_case TEXT
)
''')

# Experience table
c.execute('''
CREATE TABLE experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT, job_title TEXT NOT NULL, company TEXT NOT NULL,
    start_date TEXT, end_date TEXT, description TEXT
)
''')

# Certificates table
c.execute('''
CREATE TABLE certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, issuer TEXT NOT NULL, pdf_file TEXT NOT NULL
)
''')

# Technical Platforms table
c.execute('''
CREATE TABLE technical_platforms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    link TEXT NOT NULL,
    description TEXT
)
''')

# Home Content table
c.execute('''
CREATE TABLE home_content (
    id INTEGER PRIMARY KEY,
    greeting TEXT,
    heading_prefix TEXT,
    heading_name TEXT,
    paragraph TEXT,
    hero_image TEXT
)
''')

# --- Insert Default Data ---

# Insert default admin user
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))

# Insert default empty row for 'about'
c.execute("INSERT INTO about (id) VALUES (1)")

# Insert default content for the home page
c.execute('''
INSERT INTO home_content (id, greeting, heading_prefix, heading_name, paragraph, hero_image)
VALUES (1, 'HI THERE,', 'I Am', 'Kiranya S R', 'I’m an AI & ML enthusiast currently pursuing engineering. I love creating smart solutions using AI, building personal tech tools, and exploring new technologies.', 'hero.jpg')
''')

conn.commit()
conn.close()
print("✅ Database initialized successfully with all tables.")

