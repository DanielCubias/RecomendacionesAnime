from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from AnimeData import AnimeData
from Recommender import Recommender

app = Flask(__name__)
CORS(app)

# -----------------------------
# Database credentials
# -----------------------------
DB_USERNAME = "root"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_NAME = "anime"

# -----------------------------
# Connect to MySQL with PyMySQL
# -----------------------------
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# -----------------------------
# Load anime data once at startup
# -----------------------------
anime_data = AnimeData("./rating.csv", "./anime.csv")
anime_data.filter_users()
anime_data.filter_animes()

# ----------------------------------------
# User Management
# ----------------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
            if cursor.fetchone():
                return jsonify({"error": "User already exists"}), 400

            # Insert new user with plain-text password
            cursor.execute(
                "INSERT INTO user (username, password) VALUES (%s, %s)",
                (username, password)
            )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": f"User {username} created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": "Invalid username or password"}), 401

            user_id = row['id']
    finally:
        conn.close()

    return jsonify({"message": "Login successful", "user_id": user_id})

# ----------------------------------------
# Ratings
# ----------------------------------------
@app.route("/rate", methods=["POST"])
def rate():
    data = request.get_json()
    user_id = data.get("user_id")
    anime_id = data.get("anime_id")
    rating_value = data.get("rating")

    if not all([user_id, anime_id, rating_value]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if rating exists
            cursor.execute(
                "SELECT * FROM rating WHERE user_id=%s AND anime_id=%s",
                (user_id, anime_id)
            )
            if cursor.fetchone():
                # Update rating
                cursor.execute(
                    "UPDATE rating SET rating=%s WHERE user_id=%s AND anime_id=%s",
                    (rating_value, user_id, anime_id)
                )
            else:
                # Insert rating
                cursor.execute(
                    "INSERT INTO rating (user_id, anime_id, rating) VALUES (%s, %s, %s)",
                    (user_id, anime_id, rating_value)
                )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": f"Rating for anime {anime_id} saved"})

# ----------------------------------------
# Recommendations
# ----------------------------------------
@app.route("/recommend/<int:user_id>", methods=["GET"])
def recommend(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT * FROM user WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "User not found"}), 404

            # Get user's ratings
            cursor.execute("SELECT anime_id, rating FROM rating WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            if not rows:
                return jsonify({"warning": "User has no ratings"}), 400

            user_ratings = {row['anime_id']: row['rating'] for row in rows}
    finally:
        conn.close()

    recommender = Recommender(
        ratings_user=anime_data.ratings,
        movies=anime_data.animes,
        min_user_reviews=1,
        min_anime_reviews=1
    )

    result = recommender.recommend(user_id, user_ratings)
    if not result:
        return jsonify({"warning": "No recommendations found"})

    return jsonify(result)

# ----------------------------------------
# Run App
# ----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
