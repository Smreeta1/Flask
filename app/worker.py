import redis
from rq import Worker, Queue, Connection

listen = ['scraper-tasks']
# Use the Redis service name from docker-compose
redis_conn = redis.Redis(host='127.0.0.1', port=6379)

queue = Queue(connection=redis_conn)

if __name__ == "__main__":
    with Connection(redis_conn):
        # worker = Worker([queue])
        worker=Worker(map(Queue, listen))
        print("Worker is starting...")
        worker.work()







