# import subprocess

# def start_services():
#     # Start the enqueue service
#     subprocess.Popen(['python', 'enqueue.py'])
#
#     # Start the worker service
#     subprocess.Popen(['python', 'worker.py'])

# if __name__ == '__main__':
#     start_services()

import subprocess
import logging
import time

logging.basicConfig(filename='/app/start_services.log', level=logging.INFO)

def start_services():
    try:
        logging.info('Starting enqueue.py')
        enqueue_process = subprocess.Popen(['python', 'enqueue.py'])
        
        logging.info('Starting worker.py')
        worker_process = subprocess.Popen(['python', 'worker.py'])
        
        # Keep the script running while both processes are active
        
        while True:
            time.sleep(1) #keeps the script running in a loop:otherwise the script exits immediately after starting the processes
            
    except Exception as e:
        logging.error(f'Error occurred: {e}')
    finally:
        enqueue_process.terminate()
        worker_process.terminate()

if __name__ == '__main__':
    start_services()
