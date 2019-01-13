from pathlib import Path

from django.db import connection
from django.db import transaction
import pandas

from movie_recommender.models import Movie, Genre, Tag, User

LIKE_THRESHOLD = 4

@transaction.atomic
def load(dataset_path):
    print("Loading datasets")
    path = Path(dataset_path)
    movies = pandas.read_csv(path / 'movies.csv')
    tags = pandas.read_csv(path / 'tags.csv')
    ratings = pandas.read_csv(path / 'ratings.csv')

    print("Adding movies and genres (%s movies)" % len(movies))
    genre_map = {}
    movie_objs = []
    movie_to_genre = []
    for _, movie_id, title, genres in movies.to_records():
        movie_objs.append(Movie(title=title, pk=movie_id))

        genre_list = [] if genres.startswith('(') else genres.split('|')

        for genre in genre_list:
            if genre not in genre_map:
                genre_map[genre] = g = Genre(name=genre)
                g.save()

            movie_to_genre.append( Movie.genres.through(genre_id=genre_map[genre].id, movie_id=movie_id) )

    Movie.objects.bulk_create(movie_objs)
    Movie.genres.through.objects.bulk_create(movie_to_genre)

    # Add User <-> Movie relationship (Movie.liked_by)
    print("Adding User <-> Movie relationship")
    user_ids = set()
    movie_to_user = []
    for i, user_id, movie_id, rating, timestamp in ratings.to_records():
        if i % 10000 == 0:
            print('%d%%    ' % (100 * i / len(ratings)), end='\r')

        if rating >= LIKE_THRESHOLD:
            user_ids.add(user_id)
            movie_to_user.append( Movie.liked_by.through(user_id=user_id, movie_id=movie_id))

    print("(Creating %d users and %d relationships)" % (len(user_ids), len(movie_to_user)))
    User.objects.bulk_create([User(username='testuser_%d'%user_id, pk=user_id) for user_id in user_ids])
    Movie.liked_by.through.objects.bulk_create(movie_to_user)

    # (for this exercise, we don't care which user added the tag)
    tag_map = {}
    movie_to_tag = set()
    print("Adding tags")
    for i, user_id, movie_id, tag, timestamp in tags.to_records():
        if i % 1000 == 0:
            print('%d%%    ' % (100 * i / len(tags)), end='\r')

        tag = str(tag).lower()   # canonize
        if tag not in tag_map:
            tag_map[tag] = t = Tag(name=tag)
            t.save()

        movie_to_tag.add((tag_map[tag].id, movie_id))

    Movie.tags.through.objects.bulk_create([Movie.tags.through(movie_id=movie_id, tag_id=tag_id)
                                            for tag_id, movie_id in movie_to_tag])

