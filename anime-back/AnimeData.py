import pandas as pd

class AnimeData:
    def __init__(self, ratings_path, anime_path):
        self.ratings_path = ratings_path
        self.anime_path = anime_path
        self.ratings = pd.read_csv(ratings_path)
        self.animes = pd.read_csv(anime_path)

        self.ratings['anime_id'] = self.ratings['anime_id'].astype(int)
        self.animes['anime_id'] = self.animes['anime_id'].astype(int)

    def filter_users(self, min_reviews=300):
        counts = self.ratings['user_id'].value_counts()
        active_users = counts[counts >= min_reviews].index
        self.ratings = self.ratings[self.ratings['user_id'].isin(active_users)]

    def filter_animes(self, min_anime_reviews=1500):
        counts = self.ratings['anime_id'].value_counts()
        popular_anime = counts[counts >= min_anime_reviews].index
        self.ratings = self.ratings[self.ratings['anime_id'].isin(popular_anime)]

    def filter_genre(self, genre=""):
        if genre.strip():
            genre_anime = self.animes[self.animes['genre'].str.contains(genre, case=False, na=False)]
            self.ratings = self.ratings[self.ratings['anime_id'].isin(genre_anime['anime_id'])]

    def merge_ratings(self):
        return pd.merge(
            self.ratings.rename(columns={'rating': 'rating_user'}),
            self.animes.rename(columns={'rating': 'rating_anime'}),
            on='anime_id',
            how='inner'
        )
