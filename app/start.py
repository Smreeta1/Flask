from flask import Flask, request, render_template, redirect, url_for
from redis import Redis
from rq import Queue
from tasks import scrape_url

app = Flask(__name__)

# Connect to Redis
redis_conn = Redis(host='127.0.0.1', port=6379)
q = Queue('scraper-tasks', connection=redis_conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    if not url:
        return "URL is required", 400
    
    # Enqueue the scraping task
    job = q.enqueue(scrape_url, url)
    return redirect(url_for('get_result', job_id=job.get_id()))

@app.route('/result/<job_id>')
def get_result(job_id):
    job = q.fetch_job(job_id)
    if job:
        if job.is_finished:
            paragraphs, title = job.result
        elif job.is_failed:
            paragraphs = ["An error occurred while processing the job."]
            title = "Error"
        else:
            paragraphs = ["Processing..."]
            title = "Processing..."
    else:
        paragraphs = ["Job not found."]
        title = "Error"
    return render_template('scrape-results.html', paragraphs=paragraphs, title=title)

if __name__ == '__main__':
    app.run(debug=True)
