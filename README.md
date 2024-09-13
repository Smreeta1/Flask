## URL Scrape API

## API Endpoints

- **Home**: `GET http://127.0.0.1:8008/`
  - Response: 
    ```
    {"message": "Welcome to the URL Scrape API!"}
    ```

- **Add URL for Scraping**: `POST http://127.0.0.1:8008/scrape?url=https://example.com`
  - Response: 
    ```
    {
      "message": "Task added.",
      "job_id": "your_job_id",
      "queue_length": 1,
      "result_url": "http://127.0.0.1:8008/result"
    }
    ```

- **Check Scrape Result**: `GET http://127.0.0.1:8008/result`
  - Possible responses:
    - **Finished**:
      ```
      {"title": "Title", "paragraphs": ["Text"], "queue_length": 0}
      ```
    - **Processing**:
      ```
      {"message": "Processing...", "queue_length": 1}
      ```
    - **Failed**:
      ```
      {"error": "An error occurred."}
      ```

- **View Queued URLs**: `GET http://127.0.0.1:8008/queued-urls`
  - Response: 
    ```
    {"queued_urls": ["https://example.com"]}
    ```

## Files

- **`start.py`**: Flask application entry point.
- **`worker.py`**: Redis Queue (RQ) worker handling background jobs.
- **`tasks.py`**: Functions for scraping URLs.
