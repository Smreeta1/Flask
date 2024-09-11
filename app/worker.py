import redis
import logging
from rq import Worker, Queue, Connection

# Configure Redis connection
redis_conn = redis.Redis(host='redis', port=6379)

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(map(Queue, ['default']), connection=redis_conn)    
        print("Worker is starting...")
        worker.work()
