import pandas as pd

class Recommender:

    def __init__(self, ratings_user=None, movies=None, min_user_reviews=300, min_anime_reviews=1500, genre=""):
        if ratings_user is None or movies is None:
            raise ValueError("You must provide ratings_user and movies DataFrames")
        
        self.ratings_user = ratings_user
        self.movies = movies
        self.min_user_reviews = min_user_reviews
        self.min_anime_reviews = min_anime_reviews
        self.genre = genre

        self.userRatings = self._prepare_user_item_matrix()

    def _prepare_user_item_matrix(self):
        ratings_user = self.ratings_user.copy()
        movies = self.movies.copy()

        # Filter active users
        user_review_counts = ratings_user['user_id'].value_counts()
        active_users = user_review_counts[user_review_counts >= self.min_user_reviews].index
        ratings_user = ratings_user[ratings_user['user_id'].isin(active_users)]

        # Filter popular anime
        anime_review_counts = ratings_user['anime_id'].value_counts()
        popular_anime = anime_review_counts[anime_review_counts >= self.min_anime_reviews].index
        ratings_user = ratings_user[ratings_user['anime_id'].isin(popular_anime)]

        # Optional genre filtering
        if self.genre.strip():
            genre_anime = movies[movies['genre'].str.contains(self.genre, case=False, na=False)]
            ratings_user = ratings_user[ratings_user['anime_id'].isin(genre_anime['anime_id'])]

        # Merge ratings with anime info
        ratings_merged = pd.merge(
            ratings_user.rename(columns={'rating': 'rating_user'}),
            movies.rename(columns={'rating': 'rating_anime'}),
            on='anime_id',
            how='inner'
        )

        # Pivot table: rows = users, columns = anime titles, values = ratings
        user_item_matrix = ratings_merged.pivot_table(
            index='user_id',
            columns='name',
            values='rating_user'
        )
        if self.genre.strip():
            genre_anime = movies[movies['genre'].str.contains(self.genre, case=False, na=False)]

        return user_item_matrix

    def recommend(self, new_user_id, new_user_ratings):
        userRatings = self.userRatings.copy()  # fresh copy each request

        # Convert new user ratings to float
        new_user_ratings_numeric = {}
        for k, v in new_user_ratings.items():
            try:
                new_user_ratings_numeric[k] = float(v)
            except (ValueError, TypeError):
                continue  # skip invalid ratings

        # Add new user to matrix after pivoting (Option B)
        new_user_series = pd.Series(new_user_ratings_numeric, name=new_user_id)
        new_user_series = new_user_series.reindex(userRatings.columns)  # align with existing columns
        userRatings = pd.concat([userRatings, new_user_series.to_frame().T], axis=0)

        myRatings = userRatings.loc[new_user_id].dropna()

        if myRatings.empty:
            return {}

        # Compute item-item similarity
        corrMatrix = userRatings.corr(min_periods=1)
        sim_candidates = pd.Series(dtype=float)

        # Weighted score aggregation
        for anime, rating in myRatings.items():
            if anime not in corrMatrix.columns:
                continue
            sims = corrMatrix[anime].dropna()
            sims = sims.map(lambda x: x * rating)
            sim_candidates = pd.concat([sim_candidates, sims])

        if not sim_candidates.empty:
            sim_candidates.sort_values(ascending=False, inplace=True)

        # Aggregate and remove already rated anime
        sim_candidates = sim_candidates.groupby(sim_candidates.index).sum()
        sim_candidates = sim_candidates.drop(myRatings.index, errors='ignore')
        sim_candidates = pd.to_numeric(sim_candidates, errors='coerce')
        sim_candidates = sim_candidates.dropna()
        sim_candidates.sort_values(ascending=False, inplace=True)

        top_10 = sim_candidates.head(10).to_dict()
        return top_10
