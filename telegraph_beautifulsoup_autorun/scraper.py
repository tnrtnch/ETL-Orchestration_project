import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://telegraph.bg"

def fetch_articles():
    url = f"{BASE_URL}/posledni-novini"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")
    article_tags = soup.find_all("h2", class_="second-title")

    for article in article_tags:
        news_url = article.a.get("href")
        if not news_url.startswith("http"):
            news_url = BASE_URL + news_url

        r_news = requests.get(news_url, timeout=15)
        r_news.raise_for_status()
        s_news = BeautifulSoup(r_news.content, "lxml")

        header = s_news.find("section", class_="article-info")
        title = header.h1.text.strip() if header and header.h1 else "No title"
        author_tag = header.find("span", class_="article-author-name") if header else None
        author = author_tag.text.strip() if author_tag else "Unknown"

        content = s_news.find("section", class_="article-text")
        body = content.get_text(separator="\n", strip=True) if content else "No content"
        body = body.replace("0", "").replace("Сподели", "")

        yield {
            "title": title,
            "body": body,
            "author": author,
            "url": news_url,
            "scraped_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        time.sleep(1) 
