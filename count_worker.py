#actual processing of counting words happens in the worker function (count_words_at_url) defined in worker.py
#function (count_words_at_url) is executed asynchronously by a worker process managed by Redis Queue(rq)

import requests

def count_words_at_url(url):
    response = requests.get(url)
    return len(response.text.split())
