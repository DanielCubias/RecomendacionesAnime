from flask import Flask, jsonify, request as req
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/anime/", methods=["POST"])
def crearCarrera():
    # Receive user ratings from frontend
    data = req.get_json()
    print("Received data:", data)

    if not data or "ratings" not in data:
        return jsonify({"error": "Missing 'ratings' field"}), 400

    # Convert incoming ratings to dict {anime_name: rating}
    new_user_ratings = {item["name"]: item["rating"] for item in data["ratings"]}

    # --- Load datasets ---
    ratings = pd.read_csv('.\\rating.csv')
    movies = pd.read_csv('.\\anime.csv')

    # Ensure types
    ratings['anime_id'] = ratings['anime_id'].astype(int)
    movies['anime_id'] = movies['anime_id'].astype(int)

    # --- Filtering parameters ---
    min_reviews = 300         # Minimum ratings per user
    min_anime_reviews = 1500  # Minimum ratings per anime
    genre = ""                # You can make this dynamic later (req.args.get('genre'))

    # --- Filter users by min_reviews ---
    user_review_counts = ratings['user_id'].value_counts()
    active_users = user_review_counts[user_review_counts >= min_reviews].index
    ratings = ratings[ratings['user_id'].isin(active_users)]

    # --- Filter anime by min_anime_reviews ---
    anime_review_counts = ratings['anime_id'].value_counts()
    popular_anime = anime_review_counts[anime_review_counts >= min_anime_reviews].index
    ratings = ratings[ratings['anime_id'].isin(popular_anime)]

    # --- Filter by genre (optional) ---
    if genre.strip():
        genre_anime = movies[movies['genre'].str.contains(genre, case=False, na=False)]
        ratings = ratings[ratings['anime_id'].isin(genre_anime['anime_id'])]

    # --- Merge AFTER filtering ---
    ratings = pd.merge(ratings, movies, on='anime_id', how='inner')

    # --- Create user-item matrix ---
    userRatings = ratings.pivot_table(index=['user_id'], columns=['name'], values='rating')

    # --- Compute correlation matrix ---
    corrMatrix = userRatings.corr()

    # --- Add new user ---
    new_user_id = 999999
    new_user_series = pd.Series(new_user_ratings, name=new_user_id)
    new_user_series = new_user_series.reindex(userRatings.columns)
    userRatings = pd.concat([userRatings, new_user_series.to_frame().T], axis=0)

    myRatings = userRatings.loc[new_user_id].dropna()

    # --- Find similar anime ---
    simCandidates = pd.Series(dtype=float)
    for anime, rating in myRatings.items():
        if anime not in corrMatrix.columns:
            continue  # skip if this anime was filtered out
        sims = corrMatrix[anime].dropna()
        sims = sims.map(lambda x: x * rating)
        simCandidates = pd.concat([simCandidates, sims])

    simCandidates = simCandidates.groupby(simCandidates.index).sum()
    simCandidates.sort_values(inplace=True, ascending=False)

    # Remove already rated animes
    filteredSims = simCandidates.drop(myRatings.index, errors='ignore')

    # --- Return top 10 recommendations ---
    return jsonify(filteredSims.head(10).to_dict())
