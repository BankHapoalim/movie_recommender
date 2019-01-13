from itertools import islice

from django.shortcuts import render

from restless.views import Endpoint

from .models import Movie, User
from .recommender import RecommendByGenre

try:
    recommender = RecommendByGenre.load_from_db()
except:
    print("Recommender disabled (is the database offline?)")


ITEM_LIMIT = 5

class AddData(Endpoint):
    "Indicates that userId was previously interested in itemId"

    def post(self, request):
        user_id = int(request.POST['userId'])
        item_id = int(request.POST['itemId'])

        movie = Movie.objects.get(pk=item_id)
        user = User.objects.get(pk=user_id)

        movie.liked_by.add(user)
        recommender.train([[user.id, movie.id, 1]])

        return {}

class PredictInterests(Endpoint):
    "Should return a list of 5 itemIds that may be interesting to this userId."

    def get(self, request):
        user_id = int(request.GET['userId'])
        user = User.objects.get(pk=user_id)

        movies_liked = set(user.movie_set.values_list('id', flat=True))
        predicted = recommender.recommend_for_user(user_id)

        return list(islice((m for m in predicted if m not in movies_liked), ITEM_LIMIT))

