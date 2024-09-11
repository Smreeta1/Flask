from flask import Flask, request, render_template, redirect, url_for
from redis import Redis
from rq import Queue
from tasks import scrape_url

app = Flask(__name__)
# redis_conn = Redis(host='127.0.0.1', port=6379) # to connect outside docker

redis_conn = Redis(host='redis', port=6379)
q = Queue('default', connection=redis_conn)
job_count_key = 'job_count'
 
def increment_job_count():
    redis_conn.incr(job_count_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return "URL is required", 400
    
    job = q.enqueue(scrape_url, url)
    redis_conn.incr('job_count')  # Increment task count in Redis
    
    q_len = len(q)
    return (f"Task added. Job ID: {job.get_id()}. "
            f"Now, {q_len} jobs in the queue.")

    
    # # Increment the job count
    # increment_job_count()
    
    # # Enqueue the scraping task
    # job = q.enqueue(scrape_url, url)
    # return redirect(url_for('get_result', job_id=job.get_id()))

@app.route('/result/<job_id>')
def get_result(job_id):
    job = q.fetch_job(job_id)
    if job:
        if job.is_finished:
            paragraphs, title = job.result
            print(f"Job Result: title={title}, paragraphs={paragraphs}")  # Debug print
            return render_template('scrape-results.html', paragraphs=paragraphs, title=title)
        elif job.is_failed:
            return render_template('scrape-results.html', paragraphs=["An error occurred while processing the job."], title="Error")
        else:
            return render_template('scrape-results.html', paragraphs=["Processing..."], title="Processing...")
    else:
        return render_template('scrape-results.html', paragraphs=["Job not found."], title="Error")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8008)
