import requests
import json
from retrieve_article import RetrieveArticle

class pull:
    #newsapi api key
    api_key = "*************************"
    @staticmethod
    def get_newsapi_articles(search_query):
        base_url = "https://newsapi.org/v2/everything"
        parameters = {
            'q': search_query,  # search query
            'sortBy': 'publishedAt',  # sort by the most recent articles
            'language': 'en',  # get English articles
            'apiKey': pull.api_key,  # your API key from NewsAPI.org
            'pageSize': 40,  # limit the number of results to 3
        }

        response = requests.get(base_url, params=parameters)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            urls = []
            with open("articles.txt", 'w', encoding='utf-8') as file:
                for i, article in enumerate(articles, start=1):
                    url = article['url']
                    content = RetrieveArticle.fetch_article_content(url)
                    file.write(f"Article {i}: {article['title']}\n")
                    file.write(f"description {i}: {article['description']}\n")
                    file.write(f"content_short {i}: {article['content']}\n")
                    file.write(f"content {i}: {content}\n")
                    file.write(f"publishedAt {i}: {article['publishedAt']}\n")
                    file.write(f"publishedBy {i}: {article['source']['name']}\n\n")
                    #file.write(json.dumps(articles, indent=4))
        else:
            print("Failed to retrieve articles")
