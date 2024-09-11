from flask import Flask, request, render_template, redirect, url_for
from redis import Redis
from rq import Queue
from tasks import scrape_url

app = Flask(__name__)
# redis_conn = Redis(host='127.0.0.1', port=6379) # to connect outside docker

redis_conn = Redis(host='redis', port=6379)
q = Queue('default', connection=redis_conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    message=None
    
    url = request.form.get('url')
    if not url:
        return "URL is required", 400
    
    task = q.enqueue(scrape_url, url)
    # redis_conn.incr('job_count')  # Increment task count in Redis
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
