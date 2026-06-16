from flask import Flask, render_template, jsonify, request, session
import requests
from datetime import datetime, timedelta
import pytz
import time
import sqlite3
import hashlib
import os
import ast

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
TZ = pytz.timezone("Europe/Tallinn")

def init_db():
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  is_admin INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  match_id TEXT NOT NULL,
                  team1_score INTEGER,
                  team2_score INTEGER,
                  points INTEGER DEFAULT 0,
                  predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  UNIQUE(user_id, match_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER UNIQUE,
                  total_points INTEGER DEFAULT 0,
                  correct_scores INTEGER DEFAULT 0,
                  correct_results INTEGER DEFAULT 0,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id TEXT PRIMARY KEY,
                  team1 TEXT,
                  team2 TEXT,
                  score TEXT,
                  utc TEXT,
                  round TEXT,
                  group_name TEXT,
                  ground TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_points(pred_score1, pred_score2, actual_score1, actual_score2):
    if pred_score1 == actual_score1 and pred_score2 == actual_score2:
        return 3
    elif (pred_score1 > pred_score2 and actual_score1 > actual_score2) or \
         (pred_score1 < pred_score2 and actual_score1 < actual_score2) or \
         (pred_score1 == pred_score2 and actual_score1 == actual_score2):
        return 1
    return 0

def update_user_points(user_id):
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    
    c.execute('''SELECT p.team1_score, p.team2_score, m.score 
                 FROM predictions p
                 JOIN matches m ON p.match_id = m.id
                 WHERE p.user_id = ? AND m.score IS NOT NULL''', (user_id,))
    
    predictions = c.fetchall()
    total_points = 0
    correct_scores = 0
    correct_results = 0
    
    for pred in predictions:
        pred_score1, pred_score2 = pred[0], pred[1]
        actual_score = pred[2]
        if actual_score:
            actual_score_list = ast.literal_eval(actual_score)
            actual_score1, actual_score2 = actual_score_list[0], actual_score_list[1]
            points = calculate_points(pred_score1, pred_score2, actual_score1, actual_score2)
            total_points += points
            if points == 3:
                correct_scores += 1
            elif points == 1:
                correct_results += 1
    
    c.execute('''INSERT OR REPLACE INTO leaderboard (user_id, total_points, correct_scores, correct_results)
                 VALUES (?, ?, ?, ?)''', (user_id, total_points, correct_scores, correct_results))
    conn.commit()
    conn.close()
    return total_points

def fetch_data():
    try:
        r = requests.get(URL + f"?t={int(time.time())}")
        r.raise_for_status()
        data = r.json()
        
        conn = sqlite3.connect('worldcup.db')
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
            
            
            date_str = match["date"]
            time_str = match.get("time", "00:00")
            utc_offset = 0
            
            
            if "UTC" in time_str:
                try:
                    
                    offset_part = time_str.split("UTC")[1]
                    utc_offset = int(offset_part)
                    
                    time_str = time_str.split("UTC")[0].strip()
                except:
                    pass
            
           
            local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            
            
            utc_dt = local_dt + timedelta(hours=abs(utc_offset))
            
            
            match["utc"] = utc_dt.isoformat() + "Z"
            
            print(f"Match: {match.get('team1')} vs {match.get('team2')}")
            print(f"  Local time: {local_dt}")
            print(f"  UTC offset: {utc_offset}")
            print(f"  UTC time: {utc_dt}")
            print(f"  Estonia time: {utc_dt + timedelta(hours=3)}")
            print("---")
            
            c.execute('''INSERT OR REPLACE INTO matches (id, team1, team2, score, utc, round, group_name, ground)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (match_id, match.get("team1"), match.get("team2"), score_json, 
                       match.get("utc"), match.get("round"), match.get("group"), match.get("ground")))
            
            
            if score and score.get("ft"):
                c.execute("SELECT user_id, team1_score, team2_score FROM predictions WHERE match_id = ?", (match_id,))
                predictions = c.fetchall()
                for pred in predictions:
                    points = calculate_points(pred[1], pred[2], score["ft"][0], score["ft"][1])
                    c.execute("UPDATE predictions SET points = ? WHERE user_id = ? AND match_id = ?", 
                             (points, pred[0], match_id))
                    update_user_points(pred[0])
        
        conn.commit()
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api")
def api():
    data = fetch_data()
    if not data:
        return jsonify({"error": "Failed to fetch data"}), 500
    
    matches = []
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    c.execute("SELECT id, team1, team2, score, utc, round, group_name, ground FROM matches")
    db_matches = c.fetchall()
    conn.close()
    
    
    goals_data = {}
    if data and "matches" in data:
        for match in data["matches"]:
            match_id = f"{match.get('team1')}_vs_{match.get('team2')}_{match.get('date')}"
            goals_data[match_id] = {
                "goals1": match.get("goals1", []),
                "goals2": match.get("goals2", [])
            }
    
    for match in db_matches:
        match_id = match[0]
        score = None
        if match[3]:
            score = ast.literal_eval(match[3])
        
        
        goals = goals_data.get(match_id, {"goals1": [], "goals2": []})
        
        match_data = {
            "id": match_id,
            "team1": match[1],
            "team2": match[2],
            "score": {"ft": score} if score else None,
            "utc": match[4],
            "round": match[5],
            "group": match[6],
            "ground": match[7],
            "time": "TBD",
            "goals1": goals.get("goals1", []),
            "goals2": goals.get("goals2", [])
        }
        matches.append(match_data)
    
    return jsonify({"matches": matches})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 3:
        return jsonify({"error": "Password must be at least 3 characters"}), 400
    
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Username already exists"}), 400
    
    hashed_pw = hash_password(password)
    c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, hashed_pw, 0))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Registration successful"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if not user or user[2] != hash_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    session['user_id'] = user[0]
    session['username'] = user[1]
    session['is_admin'] = user[3]
    
    return jsonify({"success": True, "username": user[1], "is_admin": user[3]})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/me")
def get_current_user():
    if 'user_id' in session:
        return jsonify({"logged_in": True, "username": session['username'], "is_admin": session.get('is_admin', False)})
    return jsonify({"logged_in": False})

@app.route("/api/predictions", methods=["GET", "POST", "DELETE"])
def predictions():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    if request.method == "GET":
        conn = sqlite3.connect('worldcup.db')
        c = conn.cursor()
        c.execute("SELECT match_id, team1_score, team2_score, points FROM predictions WHERE user_id = ?", (session['user_id'],))
        predictions = {row[0]: {"team1Score": row[1], "team2Score": row[2], "points": row[3]} for row in c.fetchall()}
        conn.close()
        return jsonify(predictions)
    
    elif request.method == "POST":
        data = request.json
        match_id = data.get("match_id")
        team1_score = data.get("team1_score")
        team2_score = data.get("team2_score")
        
        conn = sqlite3.connect('worldcup.db')
        c = conn.cursor()
        
        c.execute("SELECT score FROM matches WHERE id = ?", (match_id,))
        match = c.fetchone()
        if match and match[0]:
            conn.close()
            return jsonify({"error": "Match already started - betting closed"}), 400
        
        c.execute("""INSERT OR REPLACE INTO predictions (user_id, match_id, team1_score, team2_score)
                     VALUES (?, ?, ?, ?)""", (session['user_id'], match_id, team1_score, team2_score))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    
    elif request.method == "DELETE":
        data = request.json
        match_id = data.get("match_id")
        
        conn = sqlite3.connect('worldcup.db')
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE user_id = ? AND match_id = ?", (session['user_id'], match_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route("/api/leaderboard")
def leaderboard():
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    c.execute('''SELECT u.username, l.total_points, l.correct_scores, l.correct_results
                 FROM leaderboard l
                 JOIN users u ON l.user_id = u.id
                 WHERE u.is_admin = 0
                 ORDER BY l.total_points DESC, l.correct_scores DESC''')
    leaderboard_data = [{"username": row[0], "total_points": row[1], "correct_scores": row[2], "correct_results": row[3]} 
                        for row in c.fetchall()]
    conn.close()
    return jsonify(leaderboard_data)

if __name__ == "__main__":
    import os

    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    print("ADMIN_PASSWORD:", ADMIN_PASSWORD)
    conn = sqlite3.connect('worldcup.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = 'pulkson'")
    if not c.fetchone():
        ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
        hashed_pw = hash_password(ADMIN_PASSWORD)
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("pulkson", hashed_pw, 1))
        conn.commit()
    conn.close()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))