from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from redis import Redis
from rq import Queue
from tasks import scrape_url
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

redis_conn = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))
q = Queue("default", connection=redis_conn)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Set session expiry time to 30 days


@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = os.urandom(16).hex()
        
        # Store the user_id in Redis with an expiration time
        redis_conn.setex(f"user_session_{session['user_id']}", timedelta(days=30), 'active')
        
    print(f"Session User ID: {session.get('user_id')}")


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
   
    print(f"URL received for scraping: {url}")
    
    user_id = session.get("user_id")
    if not user_id:
        return "User not authenticated", 403
    

    user_queued_urls_list_key = f"queued_urls_{user_id}"
    url_to_job_key = f"url_to_job_{user_id}"


    # Check if the URL has already been queued by the user
    if url.encode('utf-8') in redis_conn.lrange(user_queued_urls_list_key, 0, -1):
        return jsonify({"error": "This URL has already been queued."}), 400
    # task = q.enqueue(scrape_url, request.args.get("url"))
    task = q.enqueue(scrape_url, url)

    # Store URL in Redis list
    redis_conn.rpush(user_queued_urls_list_key, url)
    
    # Store the job ID associated with the URL
    redis_conn.hset(url_to_job_key, url, task.get_id())

    # Store the job ID in the session
    session["job_id"] = task.get_id()

    # Queue length
    q_len = len(q)
    print(
        f"Task added. Job ID: {task.get_id()}. Now, {q_len} jobs in the queue.",
        flush=True,
    )

    result_url = url_for("get_result", job_id=task.get_id(), _external=True)
    
    # JSON response after enqueuing the task
    return jsonify(
            {
                "message": "Task successfully added to the queue.",
                "job_id": task.get_id(),
                "user_id":user_id,
                "queue_length": q_len,
                "result_url": result_url,
            }),202
 
    
#View all Queued URLs by user

@app.route("/queued-urls", methods=["GET"])
def queued_urls():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 400

    user_queued_urls_list_key = f"queued_urls_{user_id}"
    

    # Retrieve URLs from Redis
    urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    urls = [url.decode("utf-8") for url in urls]

    return jsonify({"queued_urls": urls,
                    "for the user_session_id":user_id})

# View Scraped Results

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
    
    # Define the Redis keys for this user
    user_queued_urls_list_key = f"queued_urls_{user_id}"
    url_to_job_key = f"url_to_job_{user_id}"
    
    # Fetch job ID from the URL
    job_id = redis_conn.hget(url_to_job_key, url)
    if not job_id:
        return jsonify({"error": "Job for this URL not found"}), 404

    print(f"Job ID fetched from Redis for {url}: {job_id}")
    
    
    # If job ID is not found, return an error
    if not job_id:
        return jsonify(
                        {
                        "error": f"No job associated with the URL: {url}",
                        "user_session_id":user_id,
                        "user_queued_urls_list_key":user_queued_urls_list_key,
                        "url_to_job_key ": f"url_to_job_{user_id}"
                        }
                    ),400
        
    # Decode the job ID
    job_id = job_id.decode('utf-8')
    
    # Fetch the job using the job ID from the Redis Queue
    job = q.fetch_job(job_id)
    
    # Fetch the stored URLs for the current user from Redis
    stored_urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    stored_urls = [url.decode('utf-8') for url in stored_urls]  # Decode URLs

    # Print for debugging
    print(f"Stored URLs in Redis for user {user_id}: {stored_urls}")
    print(f'Current session user_id is:{user_id}')

    if job:
        if job.is_finished:
            # Assuming the job result contains the scraped data (title and paragraphs)
            paragraphs, title = job.result
            return jsonify(
                {
                    "title": title, 
                    "paragraphs": paragraphs,
                    "stored_urls": stored_urls  # Include the stored URLs in the response
                }
            )
        elif job.is_failed:
            return jsonify({"error": "The job failed to complete."}), 500
        else:
            return jsonify({"message": "Job is still processing.", "stored_urls": stored_urls}), 202
    else:
        return jsonify({"error": f"Job {job_id} not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8008)
