from flask import Flask, session
import redis
import os
from rq import Queue
from worker import count_visits  # Import the task function

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
cache = redis.Redis(host='redis', port=6379)
queue = Queue(connection=cache)  # Create a queue to add tasks

@app.route('/')
def home():
    return "Welcome to the visit counter using redis RQ!"

@app.route('/count')
def hello():
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex()  # Create a unique user ID

    user_id = session['user_id']
    print(f"Enqueuing task for user_id: {user_id}")
    job = queue.enqueue(count_visits, user_id)  # Enqueue the task
    
    return f'User ID: {user_id}. Task is enqueued. See logs for task completion.'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
