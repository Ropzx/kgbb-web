from flask import Flask, render_template, jsonify, request, session
import requests
from datetime import datetime, timedelta
import pytz
import time
import hashlib
import os
import ast
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
TZ = pytz.timezone("Europe/Tallinn")


def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        match_id TEXT NOT NULL,
        team1_score INTEGER,
        team2_score INTEGER,
        points INTEGER DEFAULT 0,
        predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, match_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE,
        total_points INTEGER DEFAULT 0,
        correct_scores INTEGER DEFAULT 0,
        correct_results INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        team1 TEXT,
        team2 TEXT,
        score TEXT,
        utc TEXT,
        round TEXT,
        group_name TEXT,
        ground TEXT
    )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_points(p1, p2, a1, a2):
    if p1 == a1 and p2 == a2:
        return 3
    elif (p1 > p2 and a1 > a2) or (p1 < p2 and a1 < a2) or (p1 == p2 and a1 == a2):
        return 1
    return 0


def create_admin():
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        print("ADMIN_PASSWORD missing")
        return

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username = %s", ("pulkson",))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            ("pulkson", hash_password(admin_password), True)
        )
        conn.commit()

    conn.close()


def fetch_data():
    try:
        r = requests.get(URL + f"?t={int(time.time())}")
        r.raise_for_status()
        data = r.json()

        conn = get_db()
        c = conn.cursor()

        for match in data.get("matches", []):

            if match.get("team1", "").startswith(("W", "L", "1", "2", "3")) or \
               match.get("team2", "").startswith(("W", "L", "1", "2", "3")):
                continue

            match_id = f"{match.get('team1')}_vs_{match.get('team2')}_{match.get('date')}"

            score = match.get("score")
            score_json = None
            if score and score.get("ft"):
                score_json = str([score["ft"][0], score["ft"][1]])

            c.execute("""
                INSERT INTO matches (id, team1, team2, score, utc, round, group_name, ground)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                score = EXCLUDED.score
            """, (
                match_id,
                match.get("team1"),
                match.get("team2"),
                score_json,
                match.get("date"),
                match.get("round"),
                match.get("group"),
                match.get("ground")
            ))

            # update points if finished
            if score and score.get("ft"):
                c.execute("""
                    SELECT user_id, team1_score, team2_score
                    FROM predictions
                    WHERE match_id = %s
                """, (match_id,))

                preds = c.fetchall()

                for p in preds:
                    pts = calculate_points(p[1], p[2], score["ft"][0], score["ft"][1])

                    c.execute("""
                        UPDATE predictions
                        SET points = %s
                        WHERE user_id = %s AND match_id = %s
                    """, (pts, p[0], match_id))

        conn.commit()
        conn.close()
        return data

    except Exception as e:
        print("fetch error:", e)
        return None


init_db()
create_admin()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api")
def api():
    data = fetch_data()
    if not data:
        return jsonify({"error": "Failed"}), 500

    conn = get_db()
    c = conn.cursor(cursor_factory=RealDictCursor)

    c.execute("SELECT * FROM matches")
    matches = c.fetchall()

    conn.close()

    return jsonify({"matches": matches})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if len(username) < 3 or len(password) < 3:
        return jsonify({"error": "Too short"}), 400

    conn = get_db()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s,%s,%s)",
            (username, hash_password(password), False)
        )
        conn.commit()
    except:
        return jsonify({"error": "User exists"}), 400

    conn.close()
    return jsonify({"success": True})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id, username, password, is_admin FROM users WHERE username = %s", (username,))
    user = c.fetchone()

    conn.close()

    if not user or user[2] != hash_password(password):
        return jsonify({"error": "Invalid"}), 401

    session["user_id"] = user[0]
    session["username"] = user[1]
    session["is_admin"] = user[3]

    return jsonify({"success": True})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/me")
def me():
    return jsonify({
        "logged_in": "user_id" in session,
        "username": session.get("username"),
        "is_admin": session.get("is_admin", False)
    })

@app.route("/api/predictions", methods=["GET", "POST", "DELETE"])
def predictions():
    if "user_id" not in session:
        return jsonify({"error": "not logged in"}), 401

    conn = get_db()
    c = conn.cursor()

    if request.method == "GET":
        c.execute("""
            SELECT match_id, team1_score, team2_score, points
            FROM predictions
            WHERE user_id = %s
        """, (session["user_id"],))

        return jsonify(c.fetchall())

    if request.method == "POST":
        d = request.json

        c.execute("""
            INSERT INTO predictions (user_id, match_id, team1_score, team2_score)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (user_id, match_id)
            DO UPDATE SET team1_score = EXCLUDED.team1_score,
                          team2_score = EXCLUDED.team2_score
        """, (
            session["user_id"],
            d["match_id"],
            d["team1_score"],
            d["team2_score"]
        ))

        conn.commit()
        conn.close()
        return jsonify({"success": True})

    if request.method == "DELETE":
        d = request.json
        c.execute(
            "DELETE FROM predictions WHERE user_id=%s AND match_id=%s",
            (session["user_id"], d["match_id"])
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route("/api/leaderboard")
def leaderboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT u.username, l.total_points, l.correct_scores, l.correct_results
        FROM leaderboard l
        JOIN users u ON u.id = l.user_id
        ORDER BY l.total_points DESC
    """)

    data = c.fetchall()
    conn.close()

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))