from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from redis import Redis
from rq import Queue
from tasks import scrape_url
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

redis_conn = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")))
q = Queue("default", connection=redis_conn)


@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = os.urandom(16).hex()
    print(f"Session User ID: {session.get('user_id')}")


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Welcome to the URL Scrape API ! Use the /scrape endpoint to add a URL to the queue"
        }
    )


@app.route("/scrape", methods=["GET","POST"])
def scrape():

    url = request.args.get("url")  # Query parameter
    if not url:
        return jsonify({"error": "URL is required"}), 400  # URL is required check

    user_id = session.get("user_id")
    if not user_id:
        return "User not authenticated", 403

    user_queued_urls_list_key = f"queued_urls_{user_id}"

    # Enqueue the task
    task = q.enqueue(scrape_url, request.args.get("url"))

    # Store URL in Redis list
    redis_conn.rpush(user_queued_urls_list_key, url)

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
    return (
        jsonify(
            {
                "message": "Task successfully added to the queue.",
                "job_id": task.get_id(),
                "queue_length": q_len,
                "result_url": result_url,
            }
        ),
        202,
    )

@app.route("/queued-urls", methods=["GET"])
def queued_urls():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 400

    user_queued_urls_list_key = f"queued_urls_{user_id}"

    # Retrieve URLs from Redis
    urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    urls = [url.decode("utf-8") for url in urls]

    return jsonify({"queued_urls": urls})


@app.route("/result/<job_id>")
def get_result(job_id):
    
    if not job_id:
        return "Job ID not found in session", 400

    job = q.fetch_job(job_id)
    q_len = len(q)
    if job:
        if job.is_finished:
            paragraphs, title = job.result
            return jsonify(
                {"title": title, "paragraphs": paragraphs, "queue_length": q_len}
            )

        elif job.is_failed:
            return (
                jsonify({"error": "An error occurred while processing the job."}),
                500,
            )
        else:
            return jsonify({"message": "Processing...", "queue_length": q_len}), 202
    else:
        return jsonify({"error": "Job not found."}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8008)
