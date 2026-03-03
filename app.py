from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG
import os

app = Flask(__name__)
app.secret_key = 'ds_create_prompts'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects ORDER BY id DESC")
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('projects.html', projects=projects)
    return "Error: Could not connect to the database."

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        image = request.files.get('image')
        
        image_filename = 'project_placeholder.jpg'
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (title, description, image) VALUES (%s, %s, %s)",
                (title, description, image_filename)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('projects'))
        return "Error: Could not connect to the database."
    return render_template('add_project.html')

@app.route('/delete_project/<int:id>')
def delete_project(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM projects WHERE id = %s", (id,))
        result = cursor.fetchone()
        if result and result[0] != 'project_placeholder.jpg':
             try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], result[0]))
             except OSError as e:
                print(f"Error deleting file: {e}")

        cursor.execute("DELETE FROM projects WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('projects'))
    return "Error: Could not connect to the database."

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                (name, email, message)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('index') + '#contact')
        else:
            flash('Failed to send message. Please try again later.', 'error')
            return redirect(url_for('index') + '#contact')

if __name__ == '__main__':
    app.run(debug=True)
