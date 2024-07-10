from flask import Flask
import redis

app = Flask(__name__)
cache = redis.Redis(host='localhost', port=6379)

@app.route('/')
def hello():
    count = cache.incr('visits')
    return f'Hello! This page has been visited {count} times.'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

