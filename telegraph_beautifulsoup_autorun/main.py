from scraper import fetch_articles
from pipelines import SQLitePipeline

def run():
    pipeline = SQLitePipeline()
    pipeline.clear_old_articles()  

    try:
        for item in fetch_articles():
            pipeline.process_item(item)
    finally:
        pipeline.close()

if __name__ == "__main__":
    run()
