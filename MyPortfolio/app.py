from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to something secure

# Upload folder setup
UPLOAD_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- ROUTES ----------

# Home
@app.route('/')
def home():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT bio FROM about WHERE id=1')
    about = c.fetchone()
    conn.close()
    return render_template('about.html', about={'bio': about[0]} if about else {'bio': 'No bio available'})

# Projects
@app.route('/projects')
def projects():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM projects')
    rows = c.fetchall()
    conn.close()
    return render_template('projects.html', projects=[
        {
            'id': row[0], 'title': row[1], 'description': row[2],
            'tech_stack': row[3], 'github': row[4], 'demo': row[5],
            'image': row[6], 'outcome': row[7], 'tools': row[8], 'use_case': row[9]
        }
        for row in rows
    ])

# Education
@app.route('/education')
def education():
    return render_template('education.html')

# Resume
@app.route('/resume')
def resume():
    return render_template('resume.html')

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['admin'] = True
            flash('Login successful.')
            return redirect('/dashboard')
        else:
            flash('Invalid username or password.')
            return redirect('/login')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out.')
    return redirect('/')

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('dashboard.html')

# Edit About
@app.route('/admin/about/edit', methods=['GET', 'POST'])
def edit_about():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        bio = request.form['bio']
        c.execute('UPDATE about SET bio=? WHERE id=1', (bio,))
        conn.commit()
        flash('About section updated.')
        return redirect('/dashboard')

    c.execute('SELECT bio FROM about WHERE id=1')
    about = c.fetchone()
    conn.close()
    return render_template('edit_about.html', about={'bio': about[0]} if about else {'bio': ''})

# Edit Projects
@app.route('/admin/projects/edit', methods=['GET', 'POST'])
def edit_projects():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        tech = request.form['tech_stack']
        github = request.form['github']
        demo = request.form['demo']
        outcome = request.form['outcome']
        tools = request.form['tools']
        use_case = request.form['use_case']

        # Handle image upload
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        c.execute('''
            INSERT INTO projects (title, description, tech_stack, github, demo, image, outcome, tools, use_case)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, desc, tech, github, demo, image_filename, outcome, tools, use_case))

        conn.commit()
        flash('Project added.')
        return redirect('/admin/projects/edit')

    c.execute('SELECT * FROM projects')
    rows = c.fetchall()
    conn.close()
    return render_template('edit_projects.html', projects=[
        {'id': row[0], 'title': row[1]} for row in rows
    ])

# Delete Project
@app.route('/admin/projects/delete/<int:pid>')
def delete_project(pid):
    if not session.get('admin'):
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    flash('Project deleted.')
    return redirect('/admin/projects/edit')

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
