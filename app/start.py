import os
import logging
from datetime import timedelta
from flask import Flask, request,url_for, jsonify, session
from redis import Redis
from rq import Queue
from tasks import scrape_url
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

redis_conn = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))
q = Queue("default", connection=redis_conn)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Set session expiry time to 30 days

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = os.urandom(16).hex()
        
        # Store the user_id in Redis with an expiration time
        redis_conn.setex(f"user_session_{session['user_id']}", timedelta(days=30), 'active')
        
    logger.info("Session User ID: %s", session.get('user_id'))


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Welcome to the URL Scrape API ! Use the /scrape endpoint to add a URL to the queue"
        }
    )

#Enqueue task(URLs)
@app.route("/scrape", methods=["GET","POST"])
def scrape():

    url = request.args.get("url")  # Query parameter
    if not url:
        return jsonify({"error": "URL is required"}), 400  
    logger.info("URL received for scraping: %s", url)
    
    
    user_id = session.get("user_id")
    if not user_id:
        return "User not authenticated", 403
    
    # Redis keys
    user_queued_urls_list_key = f"queued_urls_{user_id}"

    queued_urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    if url.encode('utf-8') in queued_urls:
        return jsonify({"error": "This URL has already been queued."}), 400

    # Generate custom ID for the job
    custom_id =url
    
    # Enqueue the task with a custom job ID
    task = q.enqueue(scrape_url, url, meta={"custom_id": custom_id},job_id=custom_id)
    job_id = task.get_id()    # Unique job ID
    
    redis_conn.rpush(user_queued_urls_list_key,url)
    
    # Queue length
    q_len = len(q)
    logger.info("Task added. Job ID: %s. Now, %d jobs in the queue.", task.get_id(), q_len) 

    result_url = url_for("get_result", job_id=job_id, _external=True)
    
    # JSON response after enqueuing the task
    return jsonify(
            {
                "message": "Task successfully added to the queue.",
                "job_id": task.get_id(),
                "user_id":user_id,
                "queue_length": q_len,
                "result_url": result_url,
            }),202
   
#View all Queued URLs by user (through their job IDs)

@app.route("/queued-urls", methods=["GET"])
def queued_urls():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 400

    user_queued_urls_list_key = f"queued_urls_{user_id}" # List of job IDs
    
    queued_urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    urls = [url.decode("utf-8") for url in queued_urls]
                
    logger.info("User ID: %s - Queued URLs: %s", user_id, urls)
   
    return jsonify({"queued_urls": urls, "user_session_id": user_id})

# View Scraped Results using job ID

@app.route("/result/")
def get_result():
    # Retrieve the URL from the query parameter
    url = request.args.get("url")  
    
    if not url:
        return jsonify({"error": "URL not found in request"}), 400
    
    # Get the user ID from the session
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 400
    
    job_id=url
     
    # Fetch the job using the job ID from the Redis Queue
    job = q.fetch_job(job_id)   

    if job:
        if job.is_finished:
            
            paragraphs, title = job.result
            custom_id = job.meta.get("custom_id")
            logger.info("Job %s finished. Title: %s", job_id, title)
            return jsonify(
                {
                    "title": title, 
                    "paragraphs": paragraphs,
                     "custom_id": custom_id,
                     "url_to_job_key" :user_id
                     
                }
            )
        elif job.is_failed:
            logger.error("Job %s failed.", job_id)

            return jsonify({"error": "The job failed to complete."}), 500
        else:
            logger.info("Job %s is still processing.", job_id)
            return jsonify({"message": "Job is still processing."}), 202
    else:
        logger.error("Job %s not found.", job_id)
        return jsonify({"error": f"Job {job_id} not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8008)
