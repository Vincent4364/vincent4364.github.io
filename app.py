from flask import Flask, render_template, request
import sqlite3
from sqlite3 import Error
import logging
import sys

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

app = Flask(__name__)
DATABASE = 'user_times'

def connect_to_database(db_file):
    """
      Connects to IMS database by passing "IMS" when calling
    """
    try:
        con = sqlite3.connect(db_file)
        logging.info(f"{db_file} connected")
        return con
    except Error as e:
        print(f"Error! Cannot connect to database '{db_file}': {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    con = connect_to_database(DATABASE)
    cur = con.cursor()
    time = int(request.form.get('time'))
    if time:
        cur.execute("PRAGMA table_info(user_times_table)")
        schema_info = cur.fetchall()
        for column in schema_info:
            print(f"  Column Name: {column[1]}")

        logging.info(f"Received reaction time: {time} ms")  # Debug print
        cur.execute("INSERT INTO user_times_table (times) VALUES (?)", (time,))
        last_time = cur.lastrowid
        logging.info(last_time)
        con.commit()
        con.close()
        return "OK", 200
    con.close()
    return "Missing time", 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
