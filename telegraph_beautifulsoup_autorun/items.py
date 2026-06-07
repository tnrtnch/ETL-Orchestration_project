from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArticleItem:
    title: str
    body: str
    author: str
    url: str
    scraped_at: datetime
