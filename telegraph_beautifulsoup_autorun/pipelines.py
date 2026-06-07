import sqlite3
import os

DB_NAME = "/app/data/telegraph.db" 

class SQLitePipeline:
    def __init__(self):
        os.makedirs("/app/data", exist_ok=True)
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                body TEXT,
                author TEXT,
                url TEXT UNIQUE,
                scraped_at TEXT
            )
        """)
        self.conn.commit()

    def clear_old_articles(self):
        """delete data older than 1 day"""
        self.cursor.execute("""
            DELETE FROM articles
            WHERE scraped_at < datetime('now','-1 day')
        """)
        self.conn.commit()

    def process_item(self, item):
        try:
            self.cursor.execute("""
                INSERT INTO articles (title, body, author, url, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("title"),
                item.get("body"),
                item.get("author"),
                item.get("url"),
                item.get("scraped_at"),
            ))
            self.conn.commit()
            print(f"[+] Saved: {item.get('title')}")
        except sqlite3.IntegrityError:
            print(f"[!] Already exists: {item.get('url')}")
        return item

    def close(self):
        self.conn.close()

