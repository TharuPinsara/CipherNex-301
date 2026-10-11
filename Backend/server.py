#!/usr/bin/env python3
import os
import sqlite3
import hashlib
import subprocess
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="../")
CORS(app)

# Change DB_PATH to:
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctf.db")
SECRET_SALT = "NX301_ORBITAL_SECURITY_SALT_2026"

# Canonical Flag Definitions (Stored as SHA-256 Hashes)
FLAG_REGISTRY = {
    1: hashlib.sha256("CIPHERNEX{ghost_signal_recovered}".encode()).hexdigest(),
    2: hashlib.sha256("CIPHERNEX{fragmented_udp_burst_recovered}".encode()).hexdigest(),
    3: hashlib.sha256("CIPHERNEX{volatile_memory_forensics_extracted}".encode()).hexdigest(),
    4: hashlib.sha256("CIPHERNEX{orbital_telemetry_manifest_decrypted}".encode()).hexdigest(),
    5: hashlib.sha256("CIPHERNEX{audio_subcarrier_stego_recovered}".encode()).hexdigest(),
    6: hashlib.sha256("CIPHERNEX{systemd_timer_privilege_escalation_achieved}".encode()).hexdigest(),
    7: hashlib.sha256("CIPHERNEX{c2_reordered_protocol_unlocked}".encode()).hexdigest(),
    8: hashlib.sha256("CIPHERNEX{ciphernex_master_telemetry_complete}".encode()).hexdigest()
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# In backend/server.py, update the init_db() function admin seed:
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                team_name TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS solves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                team_name TEXT NOT NULL,
                stage_id INTEGER NOT NULL,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_name, stage_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS submission_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                stage_id INTEGER,
                submitted_flag TEXT,
                status TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed admin user: admin / admin1234
        admin_pass = hashlib.sha256(("admin1234" + SECRET_SALT).encode()).hexdigest()
        db.execute("""
            INSERT OR REPLACE INTO users (id, email, password_hash, team_name, is_admin)
            VALUES (1, 'admin', ?, 'FLIGHT_DIRECTOR_OPS', 1)
        """, (admin_pass,))
        db.commit()

# Add these new Admin Management routes into server.py:
@app.route('/api/admin/reset-team-all', methods=['POST'])
def admin_reset_team_all():
    data = request.json or {}
    team_name = data.get('team_name')
    if not team_name:
        return jsonify({'error': 'Missing team_name parameter.'}), 400

    with get_db() as db:
        db.execute("DELETE FROM solves WHERE team_name = ?", (team_name,))
        db.execute("DELETE FROM submission_logs WHERE team_name = ?", (team_name,))
        db.commit()
    return jsonify({'success': True, 'message': f'All telemetry progress reset for {team_name}.'})

@app.route('/api/admin/reset-team-stage', methods=['POST'])
def admin_reset_team_stage():
    data = request.json or {}
    team_name = data.get('team_name')
    stage_id = data.get('stage_id')
    if not team_name or not stage_id:
        return jsonify({'error': 'Missing team_name or stage_id.'}), 400

    with get_db() as db:
        db.execute("DELETE FROM solves WHERE team_name = ? AND stage_id >= ?", (team_name, int(stage_id)))
        db.commit()
    return jsonify({'success': True, 'message': f'Revoked Stage {stage_id}+ for {team_name}.'})

init_db()

def hash_pw(pw):
    return hashlib.sha256((pw + SECRET_SALT).encode()).hexdigest()

# ----------------- AUTH APIS -----------------

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    team_name = data.get('team_name', '').strip()

    if not email or not password or not team_name:
        return jsonify({'error': 'All fields are required.'}), 400

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (email, password_hash, team_name) VALUES (?, ?, ?)",
                (email, hash_pw(password), team_name)
            )
            db.commit()
            return jsonify({'message': 'Registration successful! Please login.'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email is already registered.'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or user['password_hash'] != hash_pw(password):
            return jsonify({'error': 'Invalid credentials.'}), 401

        # Calculate currently unlocked stage for team
        solves = db.execute("SELECT stage_id FROM solves WHERE team_name = ?", (user['team_name'],)).fetchall()
        solved_stages = [row['stage_id'] for row in solves]
        unlocked_stage = max(solved_stages) + 1 if solved_stages else 1

        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'team_name': user['team_name'],
                'is_admin': bool(user['is_admin']),
                'unlocked_stage': unlocked_stage,
                'solved_stages': solved_stages
            }
        })

# ----------------- FLAG SUBMISSION ENGINE -----------------

@app.route('/api/submit-flag', methods=['POST'])
def submit_flag():
    data = request.json or {}
    team_name = data.get('team_name')
    user_id = data.get('user_id')
    stage_id = int(data.get('stage_id', 0))
    submitted_flag = data.get('flag', '').strip()
    client_ip = request.remote_addr

    if not team_name or stage_id not in FLAG_REGISTRY:
        return jsonify({'success': False, 'message': 'Invalid parameters.'}), 400

    sub_hash = hashlib.sha256(submitted_flag.encode()).hexdigest()
    expected_hash = FLAG_REGISTRY[stage_id]
    is_correct = (sub_hash == expected_hash)

    status = "SUCCESS" if is_correct else "INCORRECT"

    with get_db() as db:
        db.execute(
            "INSERT INTO submission_logs (team_name, stage_id, submitted_flag, status, ip_address) VALUES (?, ?, ?, ?, ?)",
            (team_name, stage_id, submitted_flag, status, client_ip)
        )
        if is_correct:
            try:
                db.execute(
                    "INSERT INTO solves (user_id, team_name, stage_id) VALUES (?, ?, ?)",
                    (user_id, team_name, stage_id)
                )
                db.commit()
            except sqlite3.IntegrityError:
                pass  # Already solved by team

            solves = db.execute("SELECT stage_id FROM solves WHERE team_name = ?", (team_name,)).fetchall()
            solved_stages = [row['stage_id'] for row in solves]
            next_stage = max(solved_stages) + 1

            return jsonify({
                'success': True,
                'message': f'[+] Signature Verified! Stage {stage_id} cleared.',
                'next_stage': next_stage
            })
        else:
            db.commit()
            return jsonify({'success': False, 'message': '[-] Invalid Telemetry Signature.'}), 200

# ----------------- ADMIN DASHBOARD APIS -----------------

@app.route('/api/admin/overview', methods=['GET'])
def admin_overview():
    with get_db() as db:
        teams_query = db.execute("""
            SELECT 
                u.team_name,
                COUNT(DISTINCT u.id) as member_count,
                GROUP_CONCAT(u.email, ', ') as member_emails,
                COUNT(DISTINCT s.stage_id) as total_flags,
                GROUP_CONCAT(s.stage_id, ',') as stages_solved
            FROM users u
            LEFT JOIN solves s ON u.team_name = s.team_name
            WHERE u.is_admin = 0
            GROUP BY u.team_name
            ORDER BY total_flags DESC, s.solved_at ASC
        """).fetchall()

        logs_query = db.execute("""
            SELECT team_name, stage_id, submitted_flag, status, ip_address, created_at 
            FROM submission_logs 
            ORDER BY id DESC LIMIT 50
        """).fetchall()

        teams = []
        for row in teams_query:
            solved_list = [int(x) for x in row['stages_solved'].split(',')] if row['stages_solved'] else []
            teams.append({
                'team_name': row['team_name'],
                'member_count': row['member_count'],
                'member_emails': row['member_emails'],
                'total_flags': row['total_flags'],
                'stages_solved': solved_list
            })

        logs = [dict(row) for row in logs_query]
        return jsonify({'teams': teams, 'logs': logs})

@app.route('/api/admin/reset-stage6', methods=['POST'])
def reset_stage6():
    try:
        subprocess.run(["docker", "rm", "-f", "stage6-box"], check=True)
        subprocess.run([
            "docker", "run", "-d", "--name", "stage6-box",
            "-p", "2222:22", "--restart", "unless-stopped",
            "stage6-serviceghost"
        ], check=True)
        return jsonify({'success': True, 'message': 'Stage 6 container reset successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------- LOCAL CLEAN ROUTE SIMULATION -----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@app.route('/')
def serve_index():
    for name in ['index.html', 'Index.html']:
        if os.path.exists(os.path.join(ROOT_DIR, name)):
            return send_from_directory(ROOT_DIR, name)
    return "index.html not found", 404

@app.route('/admin')
def serve_admin():
    return send_from_directory(ROOT_DIR, 'admin.html')

@app.route('/stage<int:stage_id>')
@app.route('/stage<int:stage_id>/')
@app.route('/stage<int:stage_id>/<path:filename>')
def serve_stage(stage_id, filename="index.html"):
    stage_dir = os.path.join(ROOT_DIR, f"Stage {stage_id}", "Web", f"Stage-{stage_id}")
    if os.path.exists(stage_dir):
        return send_from_directory(stage_dir, filename)
    return f"Stage {stage_id} web directory not found", 404

@app.route('/<path:filename>')
def serve_root_files(filename):
    return send_from_directory(ROOT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


