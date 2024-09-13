from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from redis import Redis
from rq import Queue
from tasks import scrape_url
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

redis_conn = Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')))
q = Queue('default', connection=redis_conn)

@app.before_request
def before_request():
    if 'user_id' not in session:
        session['user_id'] = os.urandom(16).hex()
    print(f"Session User ID: {session.get('user_id')}")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return "URL is required", 400
    
    user_id = session.get('user_id')
    if not user_id:
        return "User not authenticated", 403
    
    user_queued_urls_list_key = f'queued_urls_{user_id}'

    task = q.enqueue(scrape_url, url)
    
    # Store URL in Redis list 
    redis_conn.rpush(user_queued_urls_list_key, url)
    
    q_len = len(q)
    print(f"Task added. Job ID: {task.get_id()}. Now, {q_len} jobs in the queue.", flush=True)

    return redirect(url_for('get_result', job_id=task.get_id()))


@app.route('/queued-urls', methods=['GET'])
def queued_urls():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 400

    user_queued_urls_list_key = f'queued_urls_{user_id}'

    # Retrieve URLs from Redis
    urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    urls = [url.decode('utf-8') for url in urls]

    # Retrieve URLs from session
    session_urls = session.get('urls', [])

    print(f"Redis URLs: {urls}")
    print(f"Session URLs: {session_urls}")

    return jsonify({'queued_urls': urls})


@app.route('/result/<job_id>')
def get_result(job_id):
    job = q.fetch_job(job_id)
    q_len = len(q)
    if job:
        if job.is_finished:
            paragraphs, title = job.result
            print(f"Job Result: title={title}, paragraphs={paragraphs}")  # Debug print
            return render_template('scrape-results.html', paragraphs=paragraphs, title=title, queue_length=q_len)
        elif job.is_failed:
            return render_template('scrape-results.html', paragraphs=["An error occurred while processing the job."], title="Error", queue_length=q_len)
        else:
            return render_template('scrape-results.html', paragraphs=["Processing..."], title="Processing...", queue_length=q_len)
    else:
        return render_template('scrape-results.html', paragraphs=["Job not found."], title="Error", queue_length=q_len)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8008)
