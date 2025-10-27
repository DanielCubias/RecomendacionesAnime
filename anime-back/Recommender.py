import pandas as pd

class Recommender:
    """
    Collaborative Filtering Recommender for anime based on user ratings.

    Attributes:
        ratings_user (pd.DataFrame): DataFrame with columns ['user_id', 'anime_id', 'rating'].
        movies (pd.DataFrame): DataFrame with columns ['anime_id', 'name', 'genre', 'rating'].
        min_user_reviews (int): Minimum number of ratings a user must have to be included.
        min_anime_reviews (int): Minimum number of ratings an anime must have to be included.
        genre (str): Optional genre filter to only recommend anime of this genre.
        userRatings (pd.DataFrame): User-item rating matrix (users x anime titles).
    """

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
        print("[DEBUG] _prepare_user_item_matrix triggered")
        """
        Prepare the user-item matrix:
        - Filters active users and popular anime based on thresholds.
        - Optionally filters by genre.
        - Creates a pivot table with users as rows and anime titles as columns.
        """
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
        print("Initial ratings shape:", ratings_user.shape)
        print("Active users count:", len(active_users))
        print("Popular anime count:", len(popular_anime))
        if self.genre.strip():
            genre_anime = movies[movies['genre'].str.contains(self.genre, case=False, na=False)]
            print("Genre-filtered anime count:", len(genre_anime))

        print(f"[DEBUG] User-item matrix prepared with {user_item_matrix.shape[0]} users and {user_item_matrix.shape[1]} anime titles.")
        return user_item_matrix

    def recommend(self, new_user_id, new_user_ratings):
        """
        Recommend top 10 anime for a new user.

        Args:
            new_user_id (int or str): Unique identifier for the new user.
            new_user_ratings (dict): Dictionary of {anime_name: rating} for the new user.

        Returns:
            dict: Top 10 recommended anime with similarity-weighted scores.
        """
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

        print(f"[DEBUG] New user ratings added. Matrix now has {userRatings.shape[0]} users and {userRatings.shape[1]} anime titles.")
        myRatings = userRatings.loc[new_user_id].dropna()
        print(f"[DEBUG] Ratings considered for similarity computation: {myRatings}")

        if myRatings.empty:
            print("[WARNING] New user has no overlap with existing anime in matrix. Cannot compute recommendations.")
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
        print(f"[DEBUG] Top 10 recommendations: {top_10}")
        return top_10
