from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Upload folder setup
UPLOAD_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------- ROUTES -----------------

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# About Page
@app.route('/about')
def about():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('SELECT bio, name, dob, address, zip_code, email, phone, projects_completed, photo FROM about WHERE id=1')
    row = c.fetchone()
    about = {
        'bio': row[0], 'name': row[1], 'dob': row[2], 'address': row[3],
        'zip_code': row[4], 'email': row[5], 'phone': row[6],
        'projects_completed': row[7], 'photo': row[8]
    }

    c.execute('SELECT name, image FROM skills')
    skills = [{'name': s[0], 'image': s[1]} for s in c.fetchall()]
    conn.close()

    return render_template('about.html', about=about, skills=skills)

# Projects Page
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

# Education Page
@app.route('/education')
def education():
    return render_template('education.html')

# Resume Page
@app.route('/resume')
def resume():
    return render_template('resume.html')

# Contact Page
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
        data = {
            'bio': request.form['bio'],
            'name': request.form['name'],
            'dob': request.form['dob'],
            'address': request.form['address'],
            'zip_code': request.form['zip_code'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'projects_completed': int(request.form['projects_completed'])
        }

        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename:
            photo_filename = photo_file.filename
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo_file.save(photo_path)
            data['photo'] = photo_filename
            c.execute('''
                UPDATE about SET bio=?, name=?, dob=?, address=?, zip_code=?, email=?, phone=?, projects_completed=?, photo=? WHERE id=1
            ''', tuple(data.values()))
        else:
            c.execute('''
                UPDATE about SET bio=?, name=?, dob=?, address=?, zip_code=?, email=?, phone=?, projects_completed=? WHERE id=1
            ''', tuple(v for k, v in data.items()))

        conn.commit()
        flash('About section updated.')
        return redirect('/dashboard')

    c.execute('SELECT bio, name, dob, address, zip_code, email, phone, projects_completed, photo FROM about WHERE id=1')
    about = c.fetchone()
    conn.close()
    return render_template('edit_about.html', about={
        'bio': about[0], 'name': about[1], 'dob': about[2], 'address': about[3],
        'zip_code': about[4], 'email': about[5], 'phone': about[6],
        'projects_completed': about[7], 'photo': about[8]
    })

# Admin: Skills Edit
@app.route('/admin/skills/edit', methods=['GET', 'POST'])
def edit_skills():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        c.execute('INSERT INTO skills (name, image) VALUES (?, ?)', 
                  (name, image_filename))
        conn.commit()
        flash('Skill added successfully.')

    c.execute('SELECT * FROM skills')
    skills = c.fetchall()
    conn.close()
    return render_template('edit_skills.html', skills=skills)

# Admin: Delete Skill
@app.route('/admin/skills/delete/<int:skill_id>')
def delete_skill(skill_id):
    if not session.get('admin'):
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM skills WHERE id=?', (skill_id,))
    conn.commit()
    conn.close()
    flash('Skill deleted.')
    return redirect('/admin/skills/edit')

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


# ----------------- RUN APP -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
