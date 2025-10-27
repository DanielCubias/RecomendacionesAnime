from flask import Flask, jsonify, request as req
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/anime/", methods=["POST"])
def get_recommendations():
    # --- Receive ratings from frontend ---
    data = req.get_json()
    print("Received data:", data)

    if not data or "ratings" not in data:
        return jsonify({"error": "Missing 'ratings' field"}), 400

    new_user_ratings = {item["name"]: item["rating"] for item in data["ratings"]}

    # --- Load datasets ---
    ratings_user = pd.read_csv('.\\rating.csv')   # Existing user ratings
    movies = pd.read_csv('.\\anime.csv')          # Anime info

    # Ensure correct types
    ratings_user['anime_id'] = ratings_user['anime_id'].astype(int)
    movies['anime_id'] = movies['anime_id'].astype(int)

    # --- Filtering parameters ---
    min_reviews = 300
    min_anime_reviews = 1500
    genre = ""  # Optional, can be dynamic

    # --- Filter users by min_reviews ---
    user_review_counts = ratings_user['user_id'].value_counts()
    active_users = user_review_counts[user_review_counts >= min_reviews].index
    ratings_user = ratings_user[ratings_user['user_id'].isin(active_users)]

    # --- Filter anime by min_anime_reviews ---
    anime_review_counts = ratings_user['anime_id'].value_counts()
    popular_anime = anime_review_counts[anime_review_counts >= min_anime_reviews].index
    ratings_user = ratings_user[ratings_user['anime_id'].isin(popular_anime)]

    # --- Optional genre filtering ---
    if genre.strip():
        genre_anime = movies[movies['genre'].str.contains(genre, case=False, na=False)]
        ratings_user = ratings_user[ratings_user['anime_id'].isin(genre_anime['anime_id'])]

    # --- Merge AFTER filtering ---
    ratings_merged = pd.merge(
        ratings_user.rename(columns={'rating': 'rating_user'}),
        movies.rename(columns={'rating': 'rating_anime'}),
        on='anime_id',
        how='inner'
    )

    # --- Create user-item matrix ---
    userRatings = ratings_merged.pivot_table(
        index='user_id',
        columns='name',
        values='rating_user'
    )

    # --- Add new user from frontend ---
    new_user_id = 999999
    new_user_series = pd.Series(new_user_ratings, name=new_user_id)
    new_user_series = new_user_series.reindex(userRatings.columns)  # align columns
    userRatings = pd.concat([userRatings, new_user_series.to_frame().T], axis=0)
    myRatings = userRatings.loc[new_user_id].dropna()

    # --- Compute correlations ---
    corrMatrix = userRatings.corr()
    simCandidates = pd.Series(dtype=float)

    for anime, rating in myRatings.items():
        if anime not in corrMatrix.columns:
            continue
        sims = corrMatrix[anime].dropna()
        sims = sims.map(lambda x: x * rating)
        simCandidates = pd.concat([simCandidates, sims])

    simCandidates = simCandidates.groupby(simCandidates.index).sum()
    simCandidates = simCandidates.drop(myRatings.index, errors='ignore')
    simCandidates.sort_values(ascending=False, inplace=True)

    # --- Return top 10 recommendations ---
    return jsonify(simCandidates.head(10).to_dict())


if __name__ == "__main__":
    app.run(debug=True)
