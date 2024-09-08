from flask import Flask,session
import redis
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') 
cache = redis.Redis(host='redis', port=6379)

@app.route('/')
def home():
    return "Welcome to the visit counter!"

@app.route('/visit')
def hello():
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex()  # Create a unique user ID

    user_id = session['user_id']
    count = cache.incr(f'visits:{user_id}')  # Increment visit count for this user
    
    # count = cache.incr('visits')
    return f'User ID: {user_id}. You visited this page {count} times.'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

