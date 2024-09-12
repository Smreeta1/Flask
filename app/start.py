from flask import Flask, request, render_template, redirect, url_for,jsonify
from redis import Redis
from rq import Queue
from tasks import scrape_url

app = Flask(__name__)
# redis_conn = Redis(host='127.0.0.1', port=6379) # to connect outside docker

redis_conn = Redis(host='redis', port=6379)
q = Queue('default', connection=redis_conn)

user_queued_urls_list_key = 'queued_urls'

@app.route('/')
def index():
    return render_template('index.html')

#List all URLs queued by users.
@app.route('/queued-urls', methods=['GET'])
def list_queued_urls():
    queued_jobs = q.jobs 
    urls = []
    urls = redis_conn.lrange(user_queued_urls_list_key, 0, -1)
    urls = [url.decode('utf-8') for url in urls]
         
    for job in queued_jobs:
        if len(job.args) > 0:
            urls.append(job.args[0])  
            
    return jsonify({'queued_urls': urls})


@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return "URL is required", 400
    
    task = q.enqueue(scrape_url, url)
    
    # Store URL enqueued by users in Redis list
    redis_conn.rpush(user_queued_urls_list_key, url)
    
    q_len = len(q)
    print(f"Task added. Job ID: {task.get_id()}. Now, {q_len} jobs in the queue.", flush=True)

    return redirect(url_for('get_result', job_id=task.get_id()))

@app.route('/result/<job_id>')
def get_result(job_id):
    job = q.fetch_job(job_id)
    q_len = len(q) 
    if job:
        if job.is_finished:
            paragraphs, title = job.result
            print(f"Job Result: title={title}, paragraphs={paragraphs}")  # Debug print
            return render_template('scrape-results.html', paragraphs=paragraphs, queue_length=q_len)
        elif job.is_failed:
            return render_template('scrape-results.html', paragraphs=["An error occurred while processing the job."], title="Error")
        else:
            return render_template('scrape-results.html', paragraphs=["Processing..."], title="Processing...",queue_length=q_len)
    else:
        return render_template('scrape-results.html', paragraphs=["Job not found."], title="Error",queue_length=q_len)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8008)
