from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from flask import render_template

app = Flask(__name__)
DB_PATH = 'bigas.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE bigas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                image TEXT,
                labels TEXT
            )
        ''')
        # Example data
        c.execute("""
            INSERT INTO bigas (name, description, image, labels) VALUES
            ('Sample Biga', 'This is a sample biga.', 'sample.jpg', 'label1,label2')
        """)
        conn.commit()
        conn.close()

@app.route('/')
def gallery():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, description, image, labels FROM bigas')
    bigas = [
        {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'image': row[3],
            'labels': row[4].split(',') if row[4] else []
        }
        for row in c.fetchall()
    ]
    conn.close()
    return render_template('gallery.html', bigas=bigas)

@app.route('/add', methods=['GET', 'POST'])
def add_biga():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.form['image']
        labels = request.form['labels']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO bigas (name, description, image, labels) VALUES (?, ?, ?, ?)',
                  (name, description, image, labels))
        conn.commit()
        conn.close()
        return redirect(url_for('gallery'))
    return render_template('add_biga.html')

def home():
    return render_template("gallery.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
