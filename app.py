from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
import sqlite3
import asyncio, aiohttp

import requests

import json

import time

from urllib.parse import quote_plus, urlencode

from os import environ as env

from dotenv import load_dotenv

from auth0.authentication import Database, GetToken
from authlib.integrations.flask_client import OAuth
import authlib

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_socketio import SocketIO

from snowflake import SnowflakeGenerator

import pprint

from extras import *
from api_cmds import *

load_dotenv()

id_gen = SnowflakeGenerator(847)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['MAX_RETRIES'] = 10
socketio = SocketIO(app)

REFRESH_COOLDOWN = 10

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

user_cache = {}

class SearchForm(FlaskForm):
    query = IntegerField('Search Query', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Search')

def get_teacher_classes(teacher_id):
    conn = sqlite3.connect('YDRC.db')
    try:   
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM classes WHERE teacher_id = ?', (teacher_id,))
        result = cursor.fetchall()
    finally:
        conn.close()
    
    if result == "0,0,0,0,0":
        return None
    
    return result

def get_student_classes(student_id):
    conn = sqlite3.connect('YDRC.db')
    try:   
        cursor = conn.cursor()
        cursor.execute('SELECT class_id FROM students WHERE student_id = ?', (student_id,))
        student_class_ids = cursor.fetchone()
        if not student_class_ids:
            return None
        
        # Sqlite3 sees the question marks as variables, not empty values
        placeholders = ', '.join('?' for _ in student_class_ids)

        query = f'SELECT * FROM classes WHERE class_id IN ({placeholders})'
        cursor.execute(query, student_class_ids)
        result = cursor.fetchall()
    finally:
        conn.close()
    
    return result

def first_time(email):
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT student_id FROM students WHERE student_email = ?', (email,))
        result = cursor.fetchone()
    finally:
        conn.close()
    
    if result:
        return result[0]
    else:
        return None

def get_name(db_type: str, thing_id: str) -> str:
    print(thing_id)
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT {db_type}_name FROM {db_type}s WHERE {db_type}_id = ?', (thing_id,))
        result = cursor.fetchone()
    finally:
        conn.close()
    if result:
        return result[0]
    else:
        return None

def get_table(db_type: str) -> list:
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {db_type}')
        result = cursor.fetchall()
    finally:
        conn.close()
    return result

def is_teacher_registered(sub):
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT teacher_name FROM teachers WHERE teacher_id = ?', (sub,))
        result = cursor.fetchone()
    finally:
        conn.close()
    return result != None

def get_user(sub):
    if sub in user_cache:
        logging.info(f"User {sub} found in cache")
        return user_cache[sub]
    
    logging.info(f"User {sub} not found in cache, fetching from Auth0")
    url = f'https://{env.get("AUTH0_DOMAIN")}/api/v2/users/{sub}'
    print(url)

    payload = {}
    headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {get_api_key()}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 404:
        return None

    response.raise_for_status()

    user = response.json()

    user_cache[sub] = user

    return user

def set_app_metadata(sub, metadata: dict):
    url = f'https://{env.get("AUTH0_DOMAIN")}/api/v2/users/{sub}'

    payload = json.dumps({"app_metadata": metadata})
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {get_api_key()}'
    }

    response = requests.request("PATCH", url, headers=headers, data=payload)
    
    response.raise_for_status()
    
    return response.status_code

def verify_email(user_id):
    url = f'https://{env.get("AUTH0_DOMAIN")}/api/v2/jobs/verification-email'

    payload = json.dumps({"identity": {"user_id": user_id}})

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {get_api_key()}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    logging.info(response.text.encode('utf8'))

@app.route('/') 
def home_page():
    if 'user' not in session or session['user'] is None:
        return redirect(url_for('login_page'))
    
    u_session = session.get('user')

    if not u_session:
        return render_template('home.html', session=u_session)

    print(f"SYSTEM ID: {first_time(u_session['userinfo']['email'])}")

    sub = u_session['userinfo']['sub']

    user = get_user(sub)

    if user:
        if user["email_verified"] == False:
            verify_email(sub)
            email_verified = False
        elif user["email_verified"] == True:
            email_verified = True
        else:
            email_verified = False
            logging.warning(f"User {sub} has invalid email_verified value: {user['email_verified']}")

        if 'app_metadata' not in user:
            print("no app_metadata found, defaulting to student account type")
            user['app_metadata'] = {'account_type': 'student'}
            set_app_metadata(sub, {'account_type': 'student'})
        
        account_type = user['app_metadata']['account_type']
        
        session['account_type'] = account_type

        if account_type == 'student':
            print("student")
            print(u_session['userinfo']['email'])
            print(sub)

            name = u_session['userinfo']['name']
            if get_name('student', sub):
                print('student name found in db')
                name = get_name('student', sub)
            
            classes = get_student_classes(sub)
            if not classes:
                classes = []
            
            return render_template('home.html',
                                   name=name,
                                   email=first_time(u_session['userinfo']['email']),
                                   sub=sub,
                                   email_verified=email_verified,
                                   classes=classes)
        elif account_type == 'teacher':
            print("teacher")
            return redirect('/teacher')
        elif account_type == 'admin':
            print("admin")
            return redirect('/admin')
        else:
            raise Exception("what the hell")
    else:
        print("no auth0 user found")
        return redirect(url_for('login_page'))

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
    except authlib.integrations.base_client.errors.OAuthError as e:
        print("OAuthError: " + str(e))
        # verify_email()
        return render_template("email_verification.html", home_page_url=url_for("home_page", _external=True))
    session["user"] = token

    return redirect(url_for("home_page"))

@app.route("/login")
def login_page():
    return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home_page", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/teacher')
def teacher():
    if not session.get('user'):
        return redirect('/login')
    if session.get('account_type') != 'teacher':
        flash(f'Teacher? Contact the person who gave you this link with your Account ID below.')
        return redirect('/')

    sub = session['user']['userinfo']['sub']
    classes = get_teacher_classes(sub) # Replace this and the getting stuff in admin() with a single function

    with sqlite3.connect("YDRC.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM teachers WHERE teacher_id != ?", (sub,))
        other_classes = cursor.fetchone()

    user = get_user(sub)

    if not user["email_verified"]:
        verify_email(sub)
        email_verified = False
    elif user["email_verified"]:
        email_verified = True
    else:
        email_verified = False
        logging.warning(f"User {sub} has invalid email_verified value: {user['email_verified']}")

    name = get_name('teacher', sub)
    if not name:
        try:
            name = session['user']['userinfo']['name']
        except KeyError:
            name = "Guest"

    return render_template('teachers.html',
                           name=name,
                           registered=is_teacher_registered(session.get('user')['userinfo']['sub']),
                           sub=sub,
                           classes=classes,
                           other_classes=other_classes,
                           email_verified=email_verified)

@app.route("/teacher/create_class", methods=['GET', 'POST'])
def create_class():
    if not session.get('user'):
        return redirect('/login')
    if session.get('account_type') != 'teacher':
        flash(f'Teacher? Contact the person who gave you this link with your Account ID below.')
        return redirect('/')

    sub = session['user']['userinfo']['sub']

    if request.method == "GET":
        name = session['user']['userinfo']['name']
        name = get_name('teacher', sub)
        if not name:
            try:
                name = session['user']['userinfo']['name']
            except KeyError:
                name = "Guest"

        return render_template('create_class.html',
                               name=name,
                               registered=is_teacher_registered(sub),
                               sub=sub)
    elif request.method == "POST":
        class_id = next(id_gen)

        class_name = request.form["class_name"]
        teach_intro = request.form["teach_intro"]
        class_sched = request.form["class_sched"]
        c_desc = request.form["c_desc"]
        c_plan = request.form["c_plan"]
        c_req = request.form["c_req"]
        other_notes = request.form["other_notes"]

        if not (class_name and teach_intro and class_sched and c_desc and c_plan and c_req):
            return redirect('/teacher?error=missing-fields')
        
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO classes (class_id, teacher_id, class_name, teacher_intro, class_schedule, class_description, class_plan, class_requirements, other_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (class_id, session.get('user')['userinfo']['sub'], class_name, teach_intro, class_sched, c_desc, c_plan, c_req, other_notes))
            cursor.execute("SELECT teacher_classes FROM teachers WHERE teacher_id = ?", (sub,))
            t_classes = cursor.fetchone()
            t_classes = list(map(int, t_classes[0].split(",")))
            if t_classes.index(0) == -1:
                flash(f'You have reached the maximum number of classes you can teach. Please contact an administrator if you need to teach more.')
                return redirect('/teacher')
            t_classes[t_classes.index(0)] = class_id
            cursor.execute("UPDATE teachers SET teacher_classes = ? WHERE teacher_id = ?", (",".join(map(str, t_classes)), sub))
            db.commit()

        return redirect('/teacher')

@app.route('/class/<int:class_id>')
def class_page(class_id):
    if not session.get('user'):
        return redirect(url_for('login_page'))
    if session.get('account_type') == 'student':
        if not first_time(session.get('user')['userinfo']['email']):
            flash(f'You must enter your information before signing up for classes.')
            return redirect(url_for('home_page'))
    if not get_user(session['user']['userinfo']['sub'])['email_verified']:
        try:
            del user_cache[session.get('user')['userinfo']['sub']]
            logging.info(f"Removed user {session.get('user')['userinfo']['sub']} from cache (Refresh Account Type)")
            get_user(session.get('user')['userinfo']['sub'])
        except KeyError:
            logging.warning(f"User {session.get('user')['userinfo']['sub']} not in cache (Refresh Account Type)")
            get_user(session.get('user')['userinfo']['sub'])
    
    if session.get('account_type') == 'student':
        conn = sqlite3.connect('YDRC.db')
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM classes WHERE class_id = ?', (class_id,))
            result = cursor.fetchone()
        finally:
            conn.close()
        
        if not result:
            flash(f'Class not found. Please try again.')
            return redirect(url_for('home_page'))
        
        sub = session['user']['userinfo']['sub']
        name = get_name('student', sub)
        if not name:
            try:
                name = session['user']['userinfo']['name']
            except KeyError:
                name = "Guest"

        return render_template(f'class_student.html',
                            enrolled=already_enrolled(class_id, sub),
                            can_enroll=can_enroll(class_id, sub),
                            name=name,
                            sub=sub,
                            class_id=class_id,
                            class_name=result[2],
                            teacher_name=get_name('teacher', result[1]),
                            teacher_intro=result[3],
                            class_schedule=result[4],
                            class_description=result[5],
                            class_plan=result[6],
                            class_requirements=result[7],
                            other_notes=result[8])
    elif session.get('account_type') == 'teacher':
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_id = ?", (class_id,))
            result = cursor.fetchone()
        
        if not result:
            flash(f'Class not found. Please try again.')
            return redirect(url_for('home_page'))
        
        sub = session['user']['userinfo']['sub']
        name = get_name(get_user(sub)['app_metadata']['account_type'], sub)
        if not name:
            try:
                name = session['user']['userinfo']['name']
            except KeyError:
                name = "Guest"
        
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()

            cursor.execute("SELECT students FROM classes WHERE class_id = ?", (class_id,))
            students = cursor.fetchone()

            if students[0]:
                students = students[0].split(",")
                cursor.execute("SELECT * FROM students WHERE student_id IN (?)", (",".join(map(str, students)),))
                students = cursor.fetchall()
            else:
                students = []
        
        return render_template(f'class_teacher.html',
                               class_owner=teacher_owns_class(sub, class_id),
                               name=name,
                               sub=sub,
                               class_id=class_id,
                               class_name=result[2],
                               teacher_name=get_name('teacher', result[1]),
                               teacher_intro=result[3],
                               class_schedule=result[4],
                               class_description=result[5],
                               class_plan=result[6],
                               class_requirements=result[7],
                               other_notes=result[8],
                               students=students)
                               
def teacher_owns_class(teacher_id, class_id):   
    with sqlite3.connect("YDRC.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT teacher_classes FROM teachers WHERE teacher_id = ?", (teacher_id,))
        result = cursor.fetchone()
        result = list(map(int, result[0].split(",")))
        if class_id in result:
            return True
        else:
            return False

@app.route('/update_class_info', methods=['POST'])
def edit_class():
    try:
        if request.method == "POST":
            # For JSON data, use request.json
            data = request.json
            class_id = data['classId']
            class_name = data['className']
            teach_intro = data['teacherIntro']
            c_desc = data['classDescription']
            class_sched = data['classSchedule']
            c_plan = data['classPlan']
            c_req = data['classRequirements']
            other_notes = data['otherNotes']

            # Database update logic here
            with sqlite3.connect("YDRC.db") as db:
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE classes 
                    SET class_name = ?,
                        teacher_intro = ?, 
                        class_description = ?, 
                        class_schedule = ?, 
                        class_plan = ?, 
                        class_requirements = ?, 
                        other_notes = ? 
                    WHERE class_id = ?""",
                    (class_name, teach_intro, c_desc, class_sched, c_plan, c_req, other_notes, str(class_id)))
                db.commit()
                logging.info(f"Updated class {class_id} info")

            return jsonify({"success": True}), 200

    except Exception as e:
        logging.error("Error updating class info")
        return jsonify({"error": "An error occurred"}), 500 

def already_enrolled(class_id, sub):
    with sqlite3.connect("YDRC.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT class_id FROM students WHERE student_id = ?", (sub,))
        result = cursor.fetchone()
        if not result:
            return False

        result = list(map(int, result[0].split(",")))
        if class_id in result:
            return True
        else:
            return False

def can_enroll(class_id, sub):
    with sqlite3.connect("YDRC.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT class_id FROM students WHERE student_id = ?", (sub,))
        result = cursor.fetchone()
        result = list(map(int, result[0].split(",")))
        try:
            result.index(0)
            return True
        except ValueError:
            return False

@app.route('/enroll/<int:class_id>', methods=['POST'])
def enroll(class_id):
    if request.method == "POST":
        sub = request.form['sub']
        if not get_name("student", sub):
            logging.error(f"User {sub} supplied an invalid student ID to enroll in class {class_id}")
            return jsonify(success=False, error="Either not a student account, did not enter information, or has an invalid ID"), 400
        
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT class_id FROM students WHERE student_id = ?", (sub,))
            result = cursor.fetchone()
            if result[0]:
                print(result)
                result = list(map(int, result[0].split(",")))
                result[result.index(0)] = class_id
                cursor.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (",".join(map(str, result)), sub))
            else:
                cursor.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (str(class_id), sub))
            cursor.execute("SELECT students FROM classes WHERE class_id = ?", (class_id,))
            students = cursor.fetchone()
            if students[0]:
                print(students)
                students = list(map(int, students[0].split(",")))
                cursor.execute("UPDATE classes SET students = ? WHERE class_id = ?", (",".join(map(str, students)), class_id))
            else:
                cursor.execute("UPDATE classes SET students = ? WHERE class_id = ?", (str(sub), class_id))
            db.commit()
            logging.info("Enrolled student " + sub + " in class " + str(class_id))
        
        return redirect(f'{url_for("class_page", class_id=class_id)}')

@app.route('/unenroll/<int:class_id>', methods=['POST'])
def unenroll(class_id):
    if request.method == "POST":
        sub = request.form['sub']
        if not get_name("student", sub):
            logging.error(f"User {sub} supplied an invalid student ID to unenroll from class {class_id}")
            return jsonify(success=False, error="Either not a student account, did not enter information, or has an invalid ID"), 400
        
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT class_id FROM students WHERE student_id = ?", (sub,))
            result = cursor.fetchone()
            if result[0]:
                print(result)
                
                result = list(map(int, result[0].split(",")))
                result[result.index(class_id)] = 0
                cursor.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (",".join(map(str, result)), sub))
            else:
                return jsonify(success=False, error="Student not enrolled in class"), 400
            cursor.execute("SELECT students FROM classes WHERE class_id = ?", (class_id,))
            students = cursor.fetchone()
            if students[0]:
                print(students)
                students = students[0].split(",")
                students.remove(sub)
                cursor.execute("UPDATE classes SET students = ? WHERE class_id = ?", (",".join(map(str, students)), class_id))
            else:
                return jsonify(success=False, error="Student not enrolled in class"), 400
            db.commit()
            logging.info("Unenrolled student " + sub + " from class " + str(class_id))
        
        return redirect(f'{url_for("class_page", class_id=class_id)}')

@app.route('/teacher_submit', methods=['POST'])
def teacher_submit():
    if request.method == "POST":
        teacher_sub = session.get('user')['userinfo']['sub']
        name = request.form['name']
        email = session.get('user')['userinfo']['email']

        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO teachers (teacher_id, teacher_name, teacher_email, teacher_classes) VALUES (?, ?, ?, ?)", (teacher_sub, name, email, "0,0,0,0,0"))
            db.commit()
        
        return redirect('/teacher')

@app.route('/admin')
def admin():
    if not session.get('user'):
        return redirect('/login')

    if get_user(session['user']['userinfo']['sub'])['app_metadata']['account_type'] != 'admin':
        print("not admin")
        flash(f'Admin? Contact the person who gave you this link with your Account ID below.')
        return redirect('/')

    sub = session['user']['userinfo']['sub']
    name = get_name('admin', sub)
    if not name:
        try:
            name = session['user']['userinfo']['name']
        except KeyError:
            name = "Guest"
    
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()
        cursor.execute('SELECT * FROM teachers')
        teachers = cursor.fetchall()
        cursor.execute('SELECT * FROM admins')
        admins = cursor.fetchall()
        cursor.execute('SELECT * FROM classes')
        classes = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    
    user = get_user(sub)

    if user["email_verified"] == False:
        verify_email(sub)
        email_verified = False
    elif user["email_verified"] == True:
        email_verified = True
    else:
        email_verified = False
        logging.warning(f"User {sub} has invalid email_verified value: {user['email_verified']}")

    return render_template('admin.html',
                           name=name,
                           sub=sub,
                           students=students,
                           teachers=teachers,
                           admins=admins,
                           classes=classes)

@app.route('/admin_submit', methods=['POST'])
def admin_submit():
    if request.method == "POST":
        admin_sub = session.get('user')['userinfo']['sub']
        name = request.form['name']
        email = session.get('user')['userinfo']['email']

        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO admins (admin_id, admin_name, admin_email) VALUES (?, ?, ?)", (admin_sub, name, email))
            db.commit()
        
        return redirect('/admin')

@app.route('/change_account_type', methods=['POST'])
def change_account_type():
    if request.method == "POST":
        if not session.get('user'):
            return jsonify(success=False, message="You are not logged in.")

        if get_user(session.get('user')['userinfo']['sub'])['app_metadata']['account_type'] != 'admin':
            return jsonify(success=False, message="You do not have permission to do this.")
        
        sub = request.form['sub']

        print(sub)
        old_type = get_user(sub)['app_metadata']['account_type']
        new_type = request.form['accountType']
        if new_type not in ['student', 'teacher', 'admin']:
            return jsonify(success=False, message="Invalid account type")
        
        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT {new_type}_id FROM {new_type}s WHERE {new_type}_id = ?", (sub,))
            if not cursor.fetchone():
                cursor.execute(f"INSERT INTO {new_type}s ({new_type}_id, active) VALUES (?, ?)", (sub, 1))
            else:
                cursor.execute(f"UPDATE {new_type}s SET active = 1 WHERE {new_type}_id = ?", (sub,))
            cursor.execute(f"UPDATE {old_type}s SET active = 0 WHERE {old_type}_id = ?", (sub,))

            if new_type == 'teacher':
                cursor.execute("UPDATE teachers SET teacher_classes = ? WHERE teacher_id = ?", ('0,0,0,0,0', sub))

            db.commit()
        
        set_app_metadata(sub, {'account_type': new_type})

        # add hyperlink to user's profile page when that's done
        return jsonify(success=True,
                       message="Account type changed successfully.",
                       old_type=old_type,
                       new_type=new_type)

@app.route('/refresh_account_type', methods=['POST'])
def refresh_account_type():
    if 'last_pressed' in session:
        elapsed_time = time.time() - session['last_pressed']
        if elapsed_time < REFRESH_COOLDOWN:
            return jsonify(cooldown_remaining=int(REFRESH_COOLDOWN - elapsed_time), refresh=False)
    
    if request.method == "POST":
        try:
            del user_cache[session.get('user')['userinfo']['sub']]
            logging.info(f"Removed user {session.get('user')['userinfo']['sub']} from cache (Refresh Account Type)")
            get_user(session.get('user')['userinfo']['sub'])
        except KeyError:
            logging.warning(f"User {session.get('user')['userinfo']['sub']} not in cache (Refresh Account Type)")
            get_user(session.get('user')['userinfo']['sub'])
        session['last_pressed'] = time.time()

    return jsonify(success=True, cooldown_remaining=REFRESH_COOLDOWN, refresh=True)

@app.route('/refresh_user', methods=['POST'])
def refresh_user():
    if request.method == "POST":
        sub = request.form['sub']
        try:
            del user_cache[sub]
            logging.info(f"Removed user {sub} from cache (Refresh User)")
            get_user(sub)
        except KeyError:
            logging.warning(f"User {sub} not in cache (Refresh User)")
            get_user(sub)
    
    return jsonify(success=True)

@app.route('/check_cooldown', methods=['GET'])
def check_cooldown():
    if 'last_pressed' in session:
        elapsed_time = time.time() - session['last_pressed']
        if elapsed_time < REFRESH_COOLDOWN:
            return jsonify(cooldown_remaining=int(REFRESH_COOLDOWN - elapsed_time))
    return jsonify(cooldown_remaining=0)

@app.route('/student_submit', methods=['POST'])
def student_submit():
    if request.method == "POST":
        student_sub = session.get('user')['userinfo']['sub']
        s_email = session.get('user')['userinfo']['email']

        name = request.form['name']
        dob = request.form['dob']
        wechat = request.form['wechat']
        p_email = request.form['p_email']

        if not (name and dob and wechat and p_email):
            print("ass")
            return redirect('/?error=missing-fields')

        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO students (student_id, student_name, student_email, student_dob, parent_wechat, parent_email, class_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (student_sub, name, s_email, dob, wechat, p_email, "0,0,0,0,0"))
            db.commit()
        
        return redirect('/')

@app.route('/class_registry')
def class_registry():
    # Login Required
    if not session.get('user'):
        return redirect(url_for('login_page'))

    sub = session['user']['userinfo']['sub']
    name = get_name('student', sub)
    if not name:
        try:
            name = session['user']['userinfo']['name']
        except KeyError:
            name = "Guest"
    
    classes = get_table('classes')
    
    return render_template('class_registry.html',
                           name=name,
                           sub=sub,
                           classes=classes)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, debug=True)
