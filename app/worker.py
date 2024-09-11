import redis
from rq import Worker, Queue, Connection

listen = ['default']
# redis_conn = redis.Redis(host='127.0.0.1', port=6379) # to connect outside docker

redis_conn = redis.Redis(host='redis', port=6379)
queue = Queue(connection=redis_conn)
job_count = 0  # Initialize job count


def increment_job_count():
    # Increment job count in Redis
    redis_conn.incr('job_count')
    job_count = redis_conn.get('job_count')
    print(f"Total jobs processed: {job_count}")

def job_handler(job, *args, **kwargs):
    # Increment job count every time a job is processed
    increment_job_count()

if __name__ == "__main__":
    with Connection(redis_conn):
        # worker = Worker([queue])
        worker = Worker(map(Queue, listen))
        print("Worker is starting...")
        worker.work()
    






