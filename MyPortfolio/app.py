from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

# ------------------ App Setup ------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Get base directory of this file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Static folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
RESUME_FOLDER = os.path.join(BASE_DIR, 'static', 'resume')
CERTIFICATES_FOLDER = os.path.join(BASE_DIR, 'static', 'certificates')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATES_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESUME_FOLDER'] = RESUME_FOLDER
app.config['CERTIFICATES_FOLDER'] = CERTIFICATES_FOLDER

# Database path
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

# Database connection helper
def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

# ------------------ DB Initialization ------------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS about (
        id INTEGER PRIMARY KEY, bio TEXT, name TEXT, dob TEXT, address TEXT, 
        zip_code TEXT, email TEXT, phone TEXT, projects_completed INTEGER, photo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, image TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, tech_stack TEXT,
        github TEXT, demo TEXT, image TEXT, outcome TEXT, tools TEXT, use_case TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_title TEXT NOT NULL, company TEXT NOT NULL, 
        start_date TEXT, end_date TEXT, description TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, issuer TEXT NOT NULL, pdf_file TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS technical_platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, link TEXT NOT NULL, description TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS home_content (
        id INTEGER PRIMARY KEY, greeting TEXT, heading_prefix TEXT, heading_name TEXT, paragraph TEXT, hero_image TEXT
    )''')

    # Insert a default 'about' row if the table is empty
    c.execute('SELECT COUNT(*) FROM about WHERE id = 1')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO about (id) VALUES (1)')
        
    # Insert a default 'home_content' row if the table is empty
    c.execute('SELECT COUNT(*) FROM home_content WHERE id = 1')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO home_content (id) VALUES (1)')

    # Insert a default admin user if the table is empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))

    conn.commit()
    conn.close()

# ------------------ PUBLIC ROUTES ------------------

@app.route('/')
def home():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM home_content WHERE id = 1')
    home_data = c.fetchone()
    conn.close()
    home_content = {
        'greeting': home_data[1], 'heading_prefix': home_data[2], 'heading_name': home_data[3],
        'paragraph': home_data[4], 'hero_image': home_data[5]
    } if home_data else {}
    return render_template('home.html', home=home_content)

@app.route('/about')
def about():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('SELECT * FROM about WHERE id=1')
    row = c.fetchone()
    about_dict = {
        'bio': row[1], 'name': row[2], 'dob': row[3], 'address': row[4],
        'zip_code': row[5], 'email': row[6], 'phone': row[7],
        'projects_completed': row[8], 'photo': row[9]
    } if row else {}

    c.execute('SELECT name, image FROM skills')
    skills = [{'name': s[0], 'image': s[1]} for s in c.fetchall()]
    conn.close()
    
    resume_filename = None
    resume_dir = app.config['RESUME_FOLDER']
    if os.path.exists(resume_dir):
        pdf_files = [f for f in os.listdir(resume_dir) if f.lower().endswith('.pdf')]
        if pdf_files:
            resume_filename = pdf_files[0]
    
    return render_template('about.html', about=about_dict, skills=skills, resume_file=resume_filename)


@app.route('/projects')
def projects():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM projects')
    projects_list = [{
        'id': r[0], 'title': r[1], 'description': r[2], 'tech_stack': r[3], 
        'github': r[4], 'demo': r[5], 'image': r[6], 'outcome': r[7], 
        'tools': r[8], 'use_case': r[9]
    } for r in c.fetchall()]
    conn.close()
    return render_template('projects.html', projects=projects_list)

@app.route('/experience')
def experience():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM experience ORDER BY id DESC')
    experiences = [{
        'id': row[0], 'job_title': row[1], 'company': row[2], 
        'start_date': row[3], 'end_date': row[4], 'description': row[5]
    } for row in c.fetchall()]
    conn.close()
    return render_template('experience.html', experiences=experiences)

@app.route('/certificates')
def certificates():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM certificates ORDER BY id DESC')
    certificates_list = [{
        'id': row[0], 'title': row[1], 'issuer': row[2], 'pdf_file': row[3]
    } for row in c.fetchall()]
    conn.close()
    return render_template('certificates.html', certificates=certificates_list)

@app.route('/technical_platforms')
def technical_platforms():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM technical_platforms ORDER BY id DESC')
    platforms = [{
        'id': row[0], 'name': row[1], 'link': row[2], 'description': row[3]
    } for row in c.fetchall()]
    conn.close()
    return render_template('technical_platforms.html', platforms=platforms)

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ------------------ AUTH & DASHBOARD ------------------
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

# ------------------ ADMIN ROUTES ------------------

@app.route('/admin/home/edit', methods=['GET', 'POST'])
def edit_home():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        greeting = request.form['greeting']
        heading_prefix = request.form['heading_prefix']
        heading_name = request.form['heading_name']
        paragraph = request.form['paragraph']
        hero_image_file = request.files.get('hero_image')
        if hero_image_file and hero_image_file.filename:
            filename = secure_filename(hero_image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            hero_image_file.save(filepath)
            c.execute('UPDATE home_content SET greeting=?, heading_prefix=?, heading_name=?, paragraph=?, hero_image=? WHERE id=1',
                      (greeting, heading_prefix, heading_name, paragraph, filename))
        else:
            c.execute('UPDATE home_content SET greeting=?, heading_prefix=?, heading_name=?, paragraph=? WHERE id=1',
                      (greeting, heading_prefix, heading_name, paragraph))
        conn.commit()
        flash('Home page content updated successfully.')
        return redirect(url_for('dashboard'))
    c.execute('SELECT * FROM home_content WHERE id = 1')
    home_data = c.fetchone()
    conn.close()
    home_content = {
        'greeting': home_data[1], 'heading_prefix': home_data[2], 'heading_name': home_data[3],
        'paragraph': home_data[4], 'hero_image': home_data[5]
    } if home_data else {}
    return render_template('edit_home.html', home=home_content)

@app.route('/admin/about/edit', methods=['GET', 'POST'])
def edit_about():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        bio = request.form['bio']
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        zip_code = request.form['zip_code']
        email = request.form['email']
        phone = request.form['phone']
        projects_completed = int(request.form['projects_completed'])
        photo_file = request.files.get('photo')

        if photo_file and photo_file.filename:
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo_file.save(photo_path)
            c.execute('''UPDATE about SET bio=?, name=?, dob=?, address=?, zip_code=?, email=?, phone=?, projects_completed=?, photo=? WHERE id=1''',
                      (bio, name, dob, address, zip_code, email, phone, projects_completed, photo_filename))
        else:
            c.execute('''UPDATE about SET bio=?, name=?, dob=?, address=?, zip_code=?, email=?, phone=?, projects_completed=? WHERE id=1''',
                      (bio, name, dob, address, zip_code, email, phone, projects_completed))
        conn.commit()
        flash('About section updated.')
        return redirect('/dashboard')

    c.execute('SELECT * FROM about WHERE id=1')
    row = c.fetchone()
    conn.close()
    about_dict = {
        'bio': row[1], 'name': row[2], 'dob': row[3], 'address': row[4],
        'zip_code': row[5], 'email': row[6], 'phone': row[7],
        'projects_completed': row[8], 'photo': row[9]
    } if row else {}
    return render_template('edit_about.html', about=about_dict)

@app.route('/admin/projects/edit', methods=['GET', 'POST'])
@app.route('/admin/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_projects(project_id=None):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        pid = request.form.get('id')
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
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        if pid:
            if image_filename:
                c.execute('''UPDATE projects SET title=?, description=?, tech_stack=?, github=?, demo=?, image=?, outcome=?, tools=?, use_case=? WHERE id=?''',
                          (title, desc, tech, github, demo, image_filename, outcome, tools, use_case, pid))
            else:
                c.execute('''UPDATE projects SET title=?, description=?, tech_stack=?, github=?, demo=?, outcome=?, tools=?, use_case=? WHERE id=?''',
                          (title, desc, tech, github, demo, outcome, tools, use_case, pid))
            flash('Project updated successfully.')
        else:
            c.execute('''INSERT INTO projects (title, description, tech_stack, github, demo, image, outcome, tools, use_case) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (title, desc, tech, github, demo, image_filename, outcome, tools, use_case))
            flash('Project added successfully.')
        
        conn.commit()
        return redirect('/admin/projects/edit')

    project_to_edit = {}
    if project_id:
        c.execute('SELECT * FROM projects WHERE id=?', (project_id,))
        row = c.fetchone()
        if row:
            project_to_edit = {
                'id': row[0], 'title': row[1], 'description': row[2], 'tech_stack': row[3],
                'github': row[4], 'demo': row[5], 'image': row[6], 'outcome': row[7],
                'tools': row[8], 'use_case': row[9]
            }

    c.execute('SELECT id, title FROM projects')
    all_projects = c.fetchall()
    conn.close()
    
    return render_template('edit_projects.html', 
                           projects=[{'id': p[0], 'title': p[1]} for p in all_projects],
                           edit_mode=bool(project_id),
                           project=project_to_edit)

@app.route('/admin/skills/edit', methods=['GET', 'POST'])
def edit_skills():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        image = request.files.get('image')
        if name and image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            c.execute('INSERT INTO skills (name, image) VALUES (?, ?)', (name, filename))
            conn.commit()
            flash('Skill added successfully!')
        else:
            flash('Both name and image are required.')
        return redirect('/admin/skills/edit')

    c.execute('SELECT * FROM skills')
    skills = c.fetchall()
    conn.close()
    return render_template('edit_skills.html', skills=skills)

@app.route('/delete_skill/<int:skill_id>')
def delete_skill(skill_id):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT image FROM skills WHERE id=?", (skill_id,))
    image_data = c.fetchone()
    if image_data and image_data[0]:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_data[0])
        if os.path.exists(image_path):
            os.remove(image_path)

    c.execute("DELETE FROM skills WHERE id=?", (skill_id,))
    conn.commit()
    conn.close()
    flash("Skill deleted successfully.")
    return redirect(url_for('edit_skills'))

@app.route('/admin/experience/edit', methods=['GET', 'POST'])
def edit_experience():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        job_title = request.form['job_title']
        company = request.form['company']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        description = request.form['description']
        c.execute('INSERT INTO experience (job_title, company, start_date, end_date, description) VALUES (?, ?, ?, ?, ?)',
                  (job_title, company, start_date, end_date, description))
        conn.commit()
        flash('Experience added successfully.')
        return redirect(url_for('edit_experience'))
    
    c.execute('SELECT * FROM experience ORDER BY id DESC')
    experiences = c.fetchall()
    conn.close()
    return render_template('edit_experience.html', experiences=experiences)

@app.route('/admin/experience/delete/<int:exp_id>')
def delete_experience(exp_id):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM experience WHERE id = ?', (exp_id,))
    conn.commit()
    conn.close()
    flash('Experience entry deleted.')
    return redirect(url_for('edit_experience'))

@app.route('/admin/certificates/edit', methods=['GET', 'POST'])
def edit_certificates():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        issuer = request.form['issuer']
        pdf_file = request.files.get('pdf_file')
        if title and issuer and pdf_file and pdf_file.filename:
            if pdf_file.filename.lower().endswith('.pdf'):
                filename = secure_filename(pdf_file.filename)
                filepath = os.path.join(app.config['CERTIFICATES_FOLDER'], filename)
                pdf_file.save(filepath)
                c.execute('INSERT INTO certificates (title, issuer, pdf_file) VALUES (?, ?, ?)', (title, issuer, filename))
                conn.commit()
                flash('Certificate added successfully.')
            else:
                flash('Invalid file type. Please upload a PDF.')
        else:
            flash('All fields are required.')
        return redirect(url_for('edit_certificates'))

    c.execute('SELECT * FROM certificates ORDER BY id DESC')
    certificates = c.fetchall()
    conn.close()
    return render_template('edit_certificates.html', certificates=certificates)

@app.route('/admin/certificates/delete/<int:cert_id>')
def delete_certificate(cert_id):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT pdf_file FROM certificates WHERE id = ?', (cert_id,))
    pdf_data = c.fetchone()
    if pdf_data and pdf_data[0]:
        filepath = os.path.join(app.config['CERTIFICATES_FOLDER'], pdf_data[0])
        if os.path.exists(filepath):
            os.remove(filepath)
            
    c.execute('DELETE FROM certificates WHERE id = ?', (cert_id,))
    conn.commit()
    conn.close()
    flash('Certificate deleted.')
    return redirect(url_for('edit_certificates'))

@app.route('/admin/platforms/edit', methods=['GET', 'POST'])
@app.route('/admin/platforms/edit/<int:platform_id>', methods=['GET', 'POST'])
def edit_platforms(platform_id=None):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        pid = request.form.get('id')
        name = request.form['name']
        link = request.form['link']
        description = request.form['description']
        
        if pid:
            c.execute('UPDATE technical_platforms SET name=?, link=?, description=? WHERE id=?', (name, link, description, pid))
            flash('Platform updated successfully.')
        else:
            c.execute('INSERT INTO technical_platforms (name, link, description) VALUES (?, ?, ?)', (name, link, description))
            flash('Platform added successfully.')
        
        conn.commit()
        return redirect(url_for('edit_platforms'))

    platform_to_edit = {}
    if platform_id:
        c.execute('SELECT * FROM technical_platforms WHERE id = ?', (platform_id,))
        row = c.fetchone()
        if row:
            platform_to_edit = {'id': row[0], 'name': row[1], 'link': row[2], 'description': row[3]}

    c.execute('SELECT * FROM technical_platforms ORDER BY id DESC')
    all_platforms = c.fetchall()
    conn.close()
    
    return render_template('edit_platforms.html', 
                           platform=platform_to_edit, 
                           platforms_list=all_platforms,
                           edit_mode=bool(platform_id))

@app.route('/admin/platforms/delete/<int:platform_id>')
def delete_platform(platform_id):
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM technical_platforms WHERE id = ?', (platform_id,))
    conn.commit()
    conn.close()
    flash('Platform link deleted.')
    return redirect(url_for('edit_platforms'))


@app.route('/admin/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if not session.get('admin'): return redirect('/login')
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            resume_dir = app.config['RESUME_FOLDER']
            for old_file in os.listdir(resume_dir):
                os.remove(os.path.join(resume_dir, old_file))
            path = os.path.join(resume_dir, filename)
            file.save(path)
            flash('Resume uploaded successfully.')
            return redirect('/dashboard')
        else:
            flash('Upload failed. Please select a valid PDF file.')
    return render_template('upload_resume.html')

@app.route('/admin/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('admin'): return redirect('/login')
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
        elif not new_username or not new_password:
            flash('New username and password cannot be empty.')
        elif new_password != confirm_password:
            flash('New passwords do not match.')
        else:
            c.execute('UPDATE users SET username=?, password=? WHERE id=?', (new_username, new_password, user[0]))
            conn.commit()
            flash('Credentials updated successfully. Please log in again.')
            session.pop('admin', None)
            return redirect('/login')

    conn.close()
    return render_template('change_password.html')

# ------------------ Run App ------------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

