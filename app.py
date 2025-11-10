from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'mini_project'
mysql = MySQL(app)
@app.route('/')
def home():
    return render_template('home.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # hash in real app!
        department = request.form['department']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        else:
            cursor.execute('INSERT INTO user (name, email, password, department) VALUES (%s, %s, %s, %s)', (name, email, password, department))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
        return render_template('register.html', msg=msg)
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['user_id']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get user basic info including role
        cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()

        # Get profile details
        cursor.execute('SELECT * FROM profile WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()

        # Get skills
        cursor.execute('''
            SELECT s.skill_name
            FROM user_skill us
            JOIN skill s ON us.skill_id = s.skill_id
            WHERE us.user_id = %s
        ''', (user_id,))
        skills = [row['skill_name'] for row in cursor.fetchall()]

        # Get publications
        cursor.execute('''
            SELECT p.title, p.year, p.journal
            FROM user_publication up
            JOIN publication p ON up.publication_id = p.publication_id
            WHERE up.user_id = %s
        ''', (user_id,))
        publications = cursor.fetchall()

        # Get projects via stored procedure
        cursor.callproc('GetUserProjects', [user_id])
        projects = cursor.fetchall()

        return render_template('dashboard.html', user=user, profile=profile, skills=skills, projects=projects, publications=publications)

    return redirect(url_for('login'))


@app.route('/add_skill', methods=['POST'])
def add_skill():
    if 'loggedin' in session:
        user_id = session['id']
        skill_name = request.form['skill'].strip()

        cursor = mysql.connection.cursor()

        # Check if skill already exists
        cursor.execute('SELECT skill_id FROM skill WHERE skill_name = %s', (skill_name,))
        skill = cursor.fetchone()

        if skill:
            skill_id = skill[0]
        else:
            # Insert new skill into skill table
            cursor.execute('INSERT INTO skill (skill_name) VALUES (%s)', (skill_name,))
            mysql.connection.commit()
            skill_id = cursor.lastrowid

        # Link skill_id and user_id in user_skill table, if not already linked
        cursor.execute('SELECT * FROM user_skill WHERE user_id = %s AND skill_id = %s', (user_id, skill_id))
        link = cursor.fetchone()

        if not link:
            cursor.execute('INSERT INTO user_skill (user_id, skill_id) VALUES (%s, %s)', (user_id, skill_id))
            mysql.connection.commit()

    return redirect(url_for('dashboard'))

@app.route('/add_project', methods=['POST'])
def add_project():
    if 'loggedin' in session:
        user_id = session['id']
        title = request.form['title'].strip()
        domain = request.form['domain'].strip()
        status = request.form['status']

        cursor = mysql.connection.cursor()

        # Insert project info
        cursor.execute('INSERT INTO project (title, domain, status) VALUES (%s, %s, %s)', (title, domain, status))
        mysql.connection.commit()
        project_id = cursor.lastrowid

        # Link project with user in junction table
        cursor.execute('INSERT INTO user_project (user_id, project_id) VALUES (%s, %s)', (user_id, project_id))
        mysql.connection.commit()

    return redirect(url_for('dashboard'))

@app.route('/add_publication', methods=['POST'])
def add_publication():
    if 'loggedin' in session:
        user_id = session['id']
        title = request.form['title'].strip()
        year = request.form['year']
        journal = request.form['journal'].strip()
        cursor = mysql.connection.cursor()

        # Add to publication table
        cursor.execute('INSERT INTO publication (title, year, journal) VALUES (%s, %s, %s)', (title, year, journal))
        mysql.connection.commit()
        publication_id = cursor.lastrowid

        # Link publication to user
        cursor.execute('INSERT INTO user_publication (user_id, publication_id) VALUES (%s, %s)', (user_id, publication_id))
        mysql.connection.commit()

    return redirect(url_for('dashboard'))

@app.route('/projects')
def projects():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM project')
    projects_list = cursor.fetchall()
    return render_template('projects.html', projects=projects_list)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get project info
    cursor.execute('SELECT * FROM project WHERE project_id=%s', (project_id,))
    project = cursor.fetchone()

    # Get user(s) owning this project by joining user_project and user
    cursor.execute('''
        SELECT u.name, u.email, u.department
        FROM user_project up
        JOIN user u ON up.user_id = u.user_id
        WHERE up.project_id = %s
    ''', (project_id,))
    owners = cursor.fetchall()

    return render_template('project_detail.html', project=project, owners=owners)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
