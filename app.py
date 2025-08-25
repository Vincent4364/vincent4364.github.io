from flask import Flask, render_template, request
from dotenv import load_dotenv
import psycopg2
import os
import logging
import sys

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

app = Flask(__name__)
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.route('/')
def index():
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT id, times, created_at FROM user_times_table ORDER BY times ASC LIMIT 20")
        rows = cur.fetchall()
        cur.close()
        con.close()

        return render_template("index.html", rows=rows)

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return "Database error", 500

@app.route('/submit', methods=['POST'])
def submit():
    time = request.form.get('time')

    if not time:
        return "Missing time", 400

    try:
        time = int(time)
    except ValueError:
        return "Invalid time", 400

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("INSERT INTO user_times_table (times) VALUES (%s)", (time,))
        con.commit()

        logging.info(f"Inserted reaction time: {time} ms")

        cur.close()
        con.close()
        return "OK", 200

    except Exception as e:
        logging.error(f"Database insert failed: {e}")
        return "Database error", 500

@app.route('/data')
def data():
    try:
        limit = request.args.get("limit")  # e.g., /data?limit=20
        show_all = request.args.get("all")  # e.g., /data?all=1

        with get_connection() as con:
            with con.cursor() as cur:
                if show_all:
                    # All-time leaderboard
                    cur.execute("SELECT id, times, created_at FROM user_times_table ORDER BY times ASC")
                elif limit:
                    # Top N leaderboard (default: 20)
                    cur.execute(
                        "SELECT id, times, created_at FROM user_times_table ORDER BY times ASC LIMIT %s",
                        (int(limit),)
                    )
                else:
                    # Default to Top 20 if nothing specified
                    cur.execute("SELECT id, times, created_at FROM user_times_table ORDER BY times ASC LIMIT 20")

                rows = cur.fetchall()

        return {
            "rows": [
                {"id": r[0], "times": r[1], "created_at": r[2].strftime("%Y-%m-%d %H:%M:%S")}
                for r in rows
            ]
        }

    except Exception as e:
        logging.error(e)
        return {"rows": []}, 500

def init_db():
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_times_table (
                        id SERIAL PRIMARY KEY,
                        times INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                con.commit()
        logging.info("Database initialized ✅")
    except Exception as e:
        logging.error(f"DB init failed: {e}")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)