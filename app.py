from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import urllib.parse as urlparse
import os

app = Flask(__name__)
# Get database URL from environment variable (Render provides DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        raise Exception('DATABASE_URL environment variable not set')
    result = urlparse.urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bigas (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            image TEXT,
            labels TEXT,
            details TEXT DEFAULT ''
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            biga_id INTEGER REFERENCES bigas(id) ON DELETE CASCADE,
            name TEXT,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Insert sample data only if table is empty
    c.execute('SELECT COUNT(*) FROM bigas')
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO bigas (name, description, image, labels, details) VALUES
            ('Sample Biga', 'This is a sample biga.', 'sample', 'label1,label2', 'This is a detailed paragraph about the sample biga.\nYou can add more paragraphs by using line breaks.')
        """)
    conn.commit()
    conn.close()

@app.route('/')
def gallery():
    conn = get_db_connection()
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
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO bigas (name, description, image, labels) VALUES (%s, %s, %s, %s)',
                  (name, description, image, labels))
        conn.commit()
        conn.close()
        return redirect(url_for('gallery'))
    return render_template('add_biga.html')

@app.route('/biga/<int:biga_id>', methods=['GET', 'POST'])
def biga_detail(biga_id):
    conn = get_db_connection()
    c = conn.cursor()
    # Handle new comment submission
    if request.method == 'POST':
        name = request.form.get('name', '').strip() or None
        text = request.form.get('text', '').strip()
        if text:
            c.execute('INSERT INTO comments (biga_id, name, text) VALUES (%s, %s, %s)',
                      (biga_id, name, text))
            conn.commit()
    # Fetch biga details
    c.execute('SELECT id, name, description, image, labels, details FROM bigas WHERE id = %s', (biga_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 'Biga not found', 404
    biga = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'image': row[3],
        'labels': row[4].split(',') if row[4] else [],
        'details': row[5] or ''
    }
    # Fetch comments
    c.execute('SELECT name, text, created_at FROM comments WHERE biga_id = %s ORDER BY created_at ASC', (biga_id,))
    comments = [
        {
            'name': r[0] if r[0] else 'Anonymous',
            'text': r[1],
            'created_at': r[2]
        }
        for r in c.fetchall()
    ]
    conn.close()
    return render_template('biga_detail.html', biga=biga, comments=comments)

def home():
    return render_template("gallery.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
