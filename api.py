import time
import os
from dotenv import load_dotenv
import bcrypt
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils import is_valid_ip, sanitize_ip
from responder import unblock_ip
from flask_cors import CORS
from datetime import timedelta
from database import conn, lock

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": ["http://localhost:3000"]}
})

jwt_secret = os.getenv("JWT_SECRET_KEY")

if not jwt_secret:
    raise ValueError("JWT_SECRET_KEY missing in .env")

app.config["JWT_SECRET_KEY"] = jwt_secret

jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
password_hash = os.getenv("ADMIN_PASSWORD_HASH")

if not ADMIN_USERNAME or not password_hash:
    raise ValueError("Missing environment variables. Check your .env file.")

ADMIN_PASSWORD_HASH = password_hash.encode()

def verify_password(password):
    return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH)

# Rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return {
        "message": "Mini SOC API is running securely",
        "status": "OK",
        "version": "1.0"
    }
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Mini SOC",
        "time": int(time.time())
    })

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests"), 429

# 🔑 Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if username != ADMIN_USERNAME:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=username)
    return jsonify({
        "access_token": token,
        "message": "Login successful"
    })

# 📊 Alerts
@app.route("/alerts")
@jwt_required()
@limiter.limit("30 per minute")
def get_alerts():
    with lock:
        cursor = conn.cursor()
        rows = cursor.execute("""
            SELECT ip, type, score, country, action, timestamp
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT 50
        """).fetchall()

    alerts = [
        {
            "ip": r[0],
            "type": r[1],
            "score": r[2],
            "country": r[3],
            "action": r[4],
            "timestamp": r[5]
        }
        for r in rows
    ]

    return jsonify(alerts)

# 🚫 Blocked IPs
@app.route("/blocked")
@jwt_required()
def get_blocked():
    with lock:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT ip FROM blocked_ips").fetchall()
    return jsonify([row[0] for row in rows])

# 🔓 Unblock (FIXED)
@app.route("/unblock", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def unblock():
    data = request.get_json(silent=True)
    if not data or "ip" not in data:
        return {"error": "IP is required"}, 400
    ip = sanitize_ip(data.get("ip"))

    if not is_valid_ip(ip):
        return {"error": "Invalid IP address"}, 400

    unblock_ip(ip)
    return {"msg": f"{ip} unblocked"}

# Run
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)