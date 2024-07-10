import time

def background_task(n):
    delay = 3
    print("Task running")
    print(f"Simulating {delay} seconds delay")
    time.sleep(delay)
    result = len(n)
    print(f"Task completed! Result: {result}")
    return result

# rq worker task_worker 
#  rq worker --url redis://localhost:6379 --verbose
'''Output:
03:12:24 Sent heartbeat to prevent worker timeout. Next one should arrive within 35 seconds.
Task running
Simulating 3 seconds delay
Task completed! Result: 4
03:12:27 Handling successful execution of job b37e9738-fc19-41c4-9b07-45684dae322f
03:12:27 default: Job OK (b37e9738-fc19-41c4-9b07-45684dae322f)
03:12:27 Result: '4'
03:12:27 Result is kept for 500 seconds
03:12:27 Sent heartbeat to prevent worker timeout. Next one should arrive within 420 seconds.03:12:27 Sent heartbeat to prevent worker timeout. Next one should arrive within 420 seconds.03:12:27 *** Listening on default...
03:12:27 Sent heartbeat to prevent worker timeout. Next one should arrive within 420 seconds.03:12:27 default: worker_enqueue.background_task('test') (24560b4a-1713-47be-b64b-e48084bb1afb)
03:12:27 Sent heartbeat to prevent worker timeout. Next one should arrive within 420 seconds.03:12:27 Sent heartbeat to prevent worker timeout. Next one should arrive within 35 seconds. 
Task running ....'''
