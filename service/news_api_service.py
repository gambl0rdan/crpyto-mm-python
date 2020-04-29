import requests
from bs4 import BeautifulSoup

class NewsApiService(object):
    # Classes
    # body-content or main-content //Independant
    # article-body // Mirror
    # story-body or story-body__inner//BBC news

    def get_article_page(self, url):
        return requests.get(url)

    def get_article_content(self, page):
        contents = ''
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            resp = soup.find_all(class_='article-body')

            if resp: # assume 1
                paragraphs = resp[0].find_all('p')
                for p in paragraphs:
                    contents = contents + p.text
        return contents