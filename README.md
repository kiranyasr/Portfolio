# Portfolio Website

This is a personal portfolio website built using Flask. It allows the admin to manage projects, skills, and resume files. Visitors can view the portfolio and download the resume.

## Features

- Admin login and logout
- Add and manage projects and skills
- Upload and download resume
- Responsive UI using HTML and CSS
- Data stored in SQLite database

## Technologies Used

- Python (Flask)
- HTML, CSS
- SQLite
- Gunicorn (for deployment)

## Project Structure

MyPortfolio/
├── static/
├── templates/
├── app.py
├── init_db.py
├── init_db.sql
├── requirements.txt
├── Procfile
└── README.md


## How to Run

1. Clone the repository
2. Create a virtual environment
3. Install the required packages
4. Initialize the database
5. Run the Flask app

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python init_db.py
python app.py
