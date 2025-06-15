from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'biga.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE biga (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                image TEXT,
                labels TEXT
            )
        ''')
        # Example data
        c.execute("""
            INSERT INTO biga (name, description, image, labels) VALUES
            ('Sample Biga', 'This is a sample biga.', 'sample.jpg', 'label1,label2')
        """)
        conn.commit()
        conn.close()

@app.route('/')
def gallery():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, description, image, labels FROM biga')
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
