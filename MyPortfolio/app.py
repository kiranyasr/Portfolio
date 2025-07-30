from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os

# ------------------ App Setup ------------------

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Get base directory of this file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Set up static folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
RESUME_FOLDER = os.path.join(BASE_DIR, 'static', 'resume')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESUME_FOLDER'] = RESUME_FOLDER

# Full path to the database
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

# Database connection helper
def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT bio, name, dob, address, zip_code, email, phone, projects_completed, photo FROM about WHERE id=1')
    row = c.fetchone()
    about = {
        'bio': row[0], 'name': row[1], 'dob': row[2], 'address': row[3],
        'zip_code': row[4], 'email': row[5], 'phone': row[6],
        'projects_completed': row[7], 'photo': row[8]
    } if row else {}
    c.execute('SELECT name, image FROM skills')
    skills = [{'name': s[0], 'image': s[1]} for s in c.fetchall()]
    conn.close()
    return render_template('about.html', about=about, skills=skills)

@app.route('/projects')
def projects():
    conn = get_db_connection()
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

@app.route('/education')
def education():
    return render_template('education.html')





@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
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

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out.')
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('dashboard.html')

# ------------------ Admin: About ------------------

@app.route('/admin/about/edit', methods=['GET', 'POST'])
def edit_about():
    if not session.get('admin'):
        return redirect('/login')
    conn = get_db_connection()
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

# ------------------ Admin: Projects ------------------

@app.route('/admin/projects/edit', methods=['GET', 'POST'])
@app.route('/admin/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_projects(project_id=None):
    if not session.get('admin'):
        return redirect('/login')
    
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        pid = request.form.get('id')  # For update
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

        if pid:  # Update existing
            if image_filename:
                c.execute('''UPDATE projects SET title=?, description=?, tech_stack=?, github=?, demo=?, image=?, outcome=?, tools=?, use_case=? WHERE id=?''',
                          (title, desc, tech, github, demo, image_filename, outcome, tools, use_case, pid))
            else:
                c.execute('''UPDATE projects SET title=?, description=?, tech_stack=?, github=?, demo=?, outcome=?, tools=?, use_case=? WHERE id=?''',
                          (title, desc, tech, github, demo, outcome, tools, use_case, pid))
            flash('Project updated successfully.')
        else:  # Add new
            c.execute('''INSERT INTO projects (title, description, tech_stack, github, demo, image, outcome, tools, use_case)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (title, desc, tech, github, demo, image_filename, outcome, tools, use_case))
            flash('Project added successfully.')

        conn.commit()
        return redirect('/admin/projects/edit')

    # Load project for editing if ID is passed
    project = {}
    if project_id:
        c.execute('SELECT * FROM projects WHERE id=?', (project_id,))
        row = c.fetchone()
        if row:
            project = {
                'id': row[0], 'title': row[1], 'description': row[2],
                'tech_stack': row[3], 'github': row[4], 'demo': row[5],
                'image': row[6], 'outcome': row[7], 'tools': row[8], 'use_case': row[9]
            }

    c.execute('SELECT * FROM projects')
    rows = c.fetchall()
    conn.close()

    return render_template('edit_projects.html',
                           projects=[{'id': row[0], 'title': row[1]} for row in rows],
                           edit_mode=bool(project_id),
                           project=project)


@app.route('/admin/projects/delete/<int:pid>')
def delete_project(pid):
    if not session.get('admin'):
        return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    flash('Project deleted.')
    return redirect('/admin/projects/edit')

# ------------------ Admin: Skills ------------------

@app.route('/admin/skills/edit', methods=['GET', 'POST'])
def edit_skills():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        image = request.files.get('image')

        if name and image and image.filename:
            filename = image.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            c.execute('INSERT INTO skills (name, image) VALUES (?, ?)', (name, filename))
            conn.commit()
            flash('Skill added successfully!')
            return redirect('/admin/skills/edit')
        else:
            flash('Both name and image are required.')

    # Load skills
    c.execute('SELECT * FROM skills')
    skills = c.fetchall()
    conn.close()
    return render_template('edit_skills.html', skills=skills)

@app.route('/delete_skill/<int:skill_id>')
def delete_skill(skill_id):
    conn = sqlite3.connect('your_database_name.db')  # change to your DB name
    cursor = conn.cursor()

    # Optional: Delete associated image file from static/images
    cursor.execute("SELECT image FROM skills WHERE id=?", (skill_id,))
    image = cursor.fetchone()
    if image and image[0]:
        image_path = os.path.join('static/images', image[0])
        if os.path.exists(image_path):
            os.remove(image_path)

    cursor.execute("DELETE FROM skills WHERE id=?", (skill_id,))
    conn.commit()
    conn.close()

    flash("Skill deleted successfully.")
    return redirect(url_for('edit_skills'))


# ------------------ Admin: Resume ------------------

@app.route('/admin/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if not session.get('admin'):
        return redirect('/login')
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith('.pdf'):
            path = os.path.join(app.config['RESUME_FOLDER'], 'Kiranya_Resume.pdf')
            file.save(path)
            flash('Resume uploaded successfully.')
            return redirect('/dashboard')
        else:
            flash('Only PDF files allowed.')
            return redirect('/admin/upload_resume')
    return render_template('upload_resume.html')

# ------------------ Admin: Change Password ------------------

@app.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('admin'):
        return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        current_username = request.form['current_username']
        current_password = request.form['current_password']
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (current_username, current_password))
        user = c.fetchone()
        if not user:
            flash('Current username or password is incorrect.')
        elif new_password != confirm_password:
            flash('New passwords do not match.')
        else:
            c.execute('UPDATE users SET username=?, password=? WHERE id=?', (new_username, new_password, user[0]))
            conn.commit()
            flash('Username and password updated successfully.')
            session.pop('admin', None)
            return redirect('/login')
    conn.close()
    return render_template('change_password.html')

# ------------------ Run App ------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
