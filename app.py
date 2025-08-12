from flask import Flask, render_template, request
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = 'times_table'

def connect_to_database(db_file):
    """
      Connects to IMS database by passing "IMS" when calling
    """
    try:
        con = sqlite3.connect(db_file)
        print(f"{db_file} connected")
        return con
    except Error as e:
        print(f"Error! Cannot connect to database '{db_file}': {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

# New route to receive data from ESP32
@app.route('/submit', methods=['POST'])
def submit():
    con = connect_to_database(DATABASE)
    cur = con.cursor()
    time = int(request.form.get('time'))
    if time:
        print(f"Received reaction time: {time} ms")  # Debug print
        cur.execute("INSERT INTO user_times VALUES (?)", (time,))
        con.commit()
        con.close()
        return "OK", 200
    con.close()
    return "Missing time", 400

if __name__ == '__main__':
    # host='0.0.0.0' makes Flask listen on your local network
    app.run(debug=True, host='0.0.0.0', port=5000)
