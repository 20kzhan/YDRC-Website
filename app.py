from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import asyncio

import json

from auth0.authentication import Database, GetToken

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

class SearchForm(FlaskForm):
    query = IntegerField('Search Query', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Search')

def get_classes(id):
    conn = sqlite3.connect('YDRC.db')
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT classes FROM main WHERE id = ?', (id,))
        result = cursor.fetchone()
    finally:
        conn.close()
    return result

@app.route('/')
def login_page():
    return render_template('home.html')

"""
@app.route('/teachers', methods=['GET', 'POST'])
def teachers():
    form = SearchForm()
    items = [0]
    error = None

    if form.validate_on_submit():
        items = get_classes(form.query.data)
        print(json.loads(items[0]))
        items = json.loads(items[0])
        if not items:
            error = "Invalid input. Please enter a valid teacher ID."

    return render_template('teachers.html', form=form, items=items, error=error)
"""
    
@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/student_submit', methods=['POST'])
def student_submit():
    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        s_email = request.form['s_email']
        dob = request.form['dob']
        wechat = request.form['wechat']
        p_email = request.form['p_email']

        with sqlite3.connect("YDRC.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO students (student_id, student_name, student_email, student_dob, parent_wechat, parent_email) VALUES (?, ?, ?, ?, ?, ?)", (id, name, s_email, dob, wechat, p_email))
            db.commit()
        
        return redirect(url_for('students'))

if __name__ == '__main__':
    app.run(debug=True)
