
from flask import Flask, request
import redis
from rq import Queue
from worker_enqueue import background_task 

app = Flask(__name__)

#Redis connection setup
redis_host = 'localhost'  
redis_port = 6379  
redis_password = None  
r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

q = Queue(connection=r) #RQ queue with redis connection

@app.route("/bg_task")
def add_task():
    if request.args.get("n"):
        job = q.enqueue(background_task, request.args.get('n'))
        q_len = len(q)
        return f"Task {job.id} added to the queue at {job.enqueued_at}. Now, {q_len} tasks in the queue."
    return "No value for 'n' provided."

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8081, debug=True)
    
# redis-server
# python3 enqueue.py
# http://127.0.0.1:8081/bg_task?n=test