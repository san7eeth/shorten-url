from flask import Flask, render_template, request, redirect, url_for
import sqlite3, string, random
import os

app = Flask(__name__)
DATABASE = 'shortener.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS urls (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            original_url TEXT NOT NULL,
                            short_code TEXT NOT NULL UNIQUE
                        )''')
init_db()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        with sqlite3.connect(DATABASE) as conn:
            result = conn.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,)).fetchone()
            if not result:
                return short_code

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        with sqlite3.connect(DATABASE) as conn:
            existing = conn.execute("SELECT short_code FROM urls WHERE original_url = ?", (original_url,)).fetchone()
            if existing:
                short_code = existing[0]
            else:
                short_code = generate_short_code()
                conn.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
        short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_url(short_code):
    with sqlite3.connect(DATABASE) as conn:
        result = conn.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,)).fetchone()
        if result:
            return redirect(result[0])
    return "Invalid short URL", 404

if __name__ == '__main__':
    app.run(debug=True)
