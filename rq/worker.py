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

'''
Output:
enqueue-worker-1  | Task completed for user_id: 916470620385fb466f259bc5464277d0, visit count: 1    
enqueue-worker-1  | 07:47:57 default: Job OK (66623f87-7802-47a1-863e-87eb7720d9f5)
enqueue-worker-1  | 07:47:57 Result is kept for 500 seconds
enqueue-worker-1  | 172.18.0.1 - - [09/Sep/2024 07:48:03] "GET /count HTTP/1.1" 200 -
enqueue-worker-1  | 07:48:03 default: worker.count_visits('916470620385fb466f259bc5464277d0') (8a97002b-6cec-490e-a1e2-e76ddfd57dd0)
enqueue-worker-1  | Task completed for user_id: 916470620385fb466f259bc5464277d0, visit count: 2
enqueue-worker-1  | 07:48:03 default: Job OK (8a97002b-6cec-490e-a1e2-e76ddfd57dd0)
enqueue-worker-1  | 07:48:03 Result is kept for 500 seconds
enqueue-worker-1  | 172.18.0.1 - - [09/Sep/2024 07:48:05] "GET /count HTTP/1.1" 200 -
enqueue-worker-1  | 07:48:05 default: worker.count_visits('916470620385fb466f259bc5464277d0') (7db72cf5-3d15-4e16-a874-93aed28b5419)
enqueue-worker-1  | Task completed for user_id: 916470620385fb466f259bc5464277d0, visit count: 3    
enqueue-worker-1  | 07:48:05 default: Job OK (7db72cf5-3d15-4e16-a874-93aed28b5419)
enqueue-worker-1  | 07:48:05 Result is kept for 500 seconds






'''