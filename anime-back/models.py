class User:
    def __init__(self, id=None, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password


class Rating:
    def __init__(self, idrating=None, user_id=None, anime_id=None, rating=None):
        self.idrating = idrating
        self.user_id = user_id
        self.anime_id = anime_id
        self.rating = rating
