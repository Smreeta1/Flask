import requests
import time
from bs4 import BeautifulSoup

def scrape_url(url):
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        time.sleep(3)
        response.raise_for_status() 
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title and text content
        title = soup.title.text if soup.title else "No Title Found"
        paragraphs = [p.get_text() for p in soup.find_all('p')] 
         
        # Print the results
        print(f"Title: {title}")
        print(f"Paragraphs: {paragraphs}")
        
        return paragraphs, title
        
    except requests.exceptions.RequestException as e:
        return ["An error occurred: " + str(e)], "Error"
