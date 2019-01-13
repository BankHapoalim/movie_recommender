import requests

ENDPOINT = 'http://127.0.0.1:8000'
USER_ID = 1 # Just an arbitrary user_id

def test():
    # Test that liking a movie removes it from the recommendations

    predicted = requests.get(ENDPOINT + '/predictInterests', {"userId": USER_ID}).json()
    for movie in predicted:
        requests.post(ENDPOINT + '/addData', {'userId': USER_ID, 'itemId': movie})

    predicted2 = requests.get(ENDPOINT + '/predictInterests', {"userId": USER_ID}).json()

    assert not (set(predicted) & set(predicted2))
    print("Test OK")

if __name__ == '__main__':
    test()
