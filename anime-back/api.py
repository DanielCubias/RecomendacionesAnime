from flask import Flask, jsonify, request as req
from flask_cors import CORS
from AnimeData import AnimeData
from Recommender import Recommender

app = Flask(__name__)
CORS(app)

# Load and filter anime data once at startup
anime_data = AnimeData(".\\rating.csv", ".\\anime.csv")
anime_data.filter_users()
anime_data.filter_animes()
# anime_data.filter_genre("Action")  # optional

@app.route("/anime/", methods=["POST"])
def get_recommendations():
    data = req.get_json()
    if not data or "ratings" not in data:
        return jsonify({"error": "Missing 'ratings' field"}), 400

    new_user_id = 999999
    new_user_ratings = {item["name"]: item["rating"] for item in data["ratings"]}

    # Create a fresh Recommender instance to ensure matrix is prepared
    recommender = Recommender(
        ratings_user=anime_data.ratings,
        movies=anime_data.animes,
        min_user_reviews=1,    # lower thresholds to avoid empty matrices
        min_anime_reviews=1
    )

    result = recommender.recommend(new_user_id, new_user_ratings)
    
    if not result:
        return jsonify({"warning": "New user has no overlap with existing anime. Cannot compute recommendations."})

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
