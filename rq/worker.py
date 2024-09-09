import redis
from rq import Worker, Queue, Connection

# Use the Redis service name from docker-compose
redis_conn = redis.Redis(host='redis', port=6379)

queue = Queue(connection=redis_conn)

def count_visits(user_id):
    cache = redis.Redis(host='redis', port=6379)
    count = cache.incr(f'visits:{user_id}')  # Increment visit count for this user
    print(f"Task completed for user_id: {user_id}, visit count: {count}")
    return count

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker([queue])
        print("Worker is starting...")
        worker.work()







