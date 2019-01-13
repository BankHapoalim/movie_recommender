from collections import defaultdict

from .models import Movie

class Recommender:
    "Abstract class, providing interface for recommenders"

    @classmethod
    def load_from_db(cls):
        "Short-hand from loading and training this class"
        recommender = cls()
        recommender.train(cls.load_db_data())
        return recommender

    @staticmethod
    def load_db_data():
        "Load the user<->movie relationships from the database, for Recommender.train"

        return [(user_id, movie.id, 1)
                for movie in Movie.objects.all()
                for user_id in movie.liked_by.values_list('id', flat=True)]

    def train(self, data):
        "Train the recommender, where data is a list of (user, movie, liked_bool) tuples (cumulative)"
        raise NotImplementedError()

    def rate(self, user_id, movie_id):
        "Predict whether the user will like this movie or not"
        raise NotImplementedError()

    def recommend_for_user(self, user_id):
        "Return a list of recommended movies, sorted by likelihood"
        raise NotImplementedError()


class RecommendByGenre(Recommender):
    """A simple but effective content-based recommender that uses genres

    It works by tallying up the score for each genre (based on movies liked),
    And then rating new movies according to the scores of their genres.
    """

    def __init__(self):
        self.movie_genres = {movie.id: movie.genres.values_list('id', flat=True)
                             for movie in Movie.objects.all() }
        self.genre_scores = defaultdict(lambda: defaultdict(int))

    def train(self, data):
        for user, movie, match in data:
            for genre in self.movie_genres[movie]:
                self.genre_scores[user][genre] += 1 if match else -1

    def rate(self, user, movie):
        return sum(self.genre_scores[user][genre] for genre in self.movie_genres[movie])

    def recommend_for_user(self, user_id):
        scored_movies = [(self.rate(user_id, movie_id), movie_id)
                         for movie_id in self.movie_genres]
        scored_movies.sort(reverse=True)
        return [movie_id for _, movie_id in scored_movies]

