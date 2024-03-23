import requests
from bs4 import BeautifulSoup

class RetrieveArticle:
    @staticmethod
    def fetch_article_content(url):
        try:
            response = requests.get(url)

        except:
            return None
            # Handle other possible errors

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # The logic here assumes the main content is within <article> tags or <p> tags
        article_content = soup.find('article')
        if not article_content:
            article_content = soup

        # Extract text from the <p> tags
        paragraphs = article_content.find_all('p')
        article_text = ' '.join(paragraph.text for paragraph in paragraphs)

        return article_text