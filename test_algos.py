from random import randrange

import numpy as np
import pandas as pd
from surprise import Dataset, Reader, KNNBasic, SVDpp

from movie_recommender.recommender import RecommendByGenre, Recommender

class RandomRecommender(Recommender):
    name = 'random'

    def train(self, data):
        pass

    def rate_bool(self, user, movie):
        return bool(randrange(2))

class GenreRecommender(RecommendByGenre):
    name = 'genre-based'

    def rate_bool(self, user, movie):
        return self.rate(user, movie) > 0


class SurpriseRecommender(Recommender):
    name = 'surprise-svdpp'

    def train(self, data):
        ratings_dict = {'itemID': data[:,1],
                        'userID': data[:,0],
                        'rating': data[:,2]}
        df = pd.DataFrame(ratings_dict)

        reader = Reader(rating_scale=(0, 1))

        data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader).build_full_trainset()
        # self.algo = KNNBasic(verbose=False)
        self.algo = SVDpp(verbose=True)
        self.algo.fit(data)

    def rate(self, user, movie):
        return self.algo.test([[user, movie, 0]])[0].est

    def rate_bool(self, user, movie):
        return self.rate(user, movie) > 0.5


RECOMMENDERS = [RandomRecommender, SurpriseRecommender, GenreRecommender]

TRAIN_EVAL_RATIO = 0.8

def test(noise_ratio=1):
    """Tests the different recommenders and prints out the results with the following metrics:

    Accuracy - native measure of how many times the recommender guessed right
    Precision - how many of the approved items would be relevant
    Recall - how many of the relevant items are detected as such
    """

    print("Testing recommenders (noise ratio: %s)" % (noise_ratio))
    print()
    data = Recommender.load_db_data()

    train_size = int(len(data) * TRAIN_EVAL_RATIO)

    data = np.array(data)
    np.random.shuffle(data)
    max_user = data[:,0].max()
    max_movie = data[:,1].max()

    train_data = data[:train_size]
    eval_data = data[train_size:]

    random_data = [(randrange(max_user), m , 0) for _, m, _ in np.concatenate([train_data]*noise_ratio)]
    train_data = np.concatenate([train_data, random_data])
    np.random.shuffle(train_data)

    random_data = [(randrange(max_user), m , 0) for _, m, _ in eval_data]
    eval_data = np.concatenate([eval_data, random_data])
    np.random.shuffle(eval_data)

    results = {}
    for recommender_cls in RECOMMENDERS:
        recommender = recommender_cls()
        try:
            recommender.train(train_data)
        except MemoryError:
            print("[%s] Memory error" % recommender.name)
            continue

        correct = 0
        tp = 0
        fp = 0
        fn = 0
        for user, movie, expected in eval_data:
            predicted = recommender.rate_bool(user, movie)

            if predicted:
                if expected:
                    tp += 1
                else:
                    fp += 1
            else:
                if expected:
                    fn += 1

            if predicted == expected:
                correct += 1

        accuracy = correct / len(eval_data)
        precision = float(tp) / (tp + fp)
        recall = float(tp) / (tp + fn)

        print("[%s] Accuracy: %.2f    Precision: %.2f   Recall: %.2f" % (
                recommender.name, accuracy, precision, recall))

        for rec, (_accuracy, _prec, _recall) in results.items():
            print('\t(Accuracy: x%.2f   Precision x%.2f  Recall x%.2f better than %s)' % (
                accuracy / _accuracy, precision / _prec, recall / _recall, rec.name))

        results[recommender] = accuracy, precision, recall
        print()

