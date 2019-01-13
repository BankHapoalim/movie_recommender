# Movie Recommender - a test project

Step 1: Clone Repo

Step 2: Create and activate virtualenv (optional but recommended)

    virtualenv -p python3 .env && . .env/bin/activate

Step 3: Get and unzip dataset

    # 100k data points (recommended for fast loading times)
    wget http://files.grouplens.org/datasets/movielens/ml-latest-small.zip && unzip ml-latest-small.zip

    OR

    # 2000k data points
    wget http://files.grouplens.org/datasets/movielens/ml-20m.zip && unzip ml-20m.zip

Step 4: Install 3rd party libraries

    pip install -r pip_requirements.txt

Step 5: Create database

    ./manage.py migrate

Step 6: Load dataset

    ./load_dataset.sh ml-latest-small

    OR

    ./load_dataset.sh ml-20m


Step 7: Run algorithm tests

    ./test_algos.sh

Step 8: Run server and test endpoints

    ./manage.py runserver 8000

    (wait for it to come up)

    python test_endpoint.py

