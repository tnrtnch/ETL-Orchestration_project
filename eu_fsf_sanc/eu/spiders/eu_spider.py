import scrapy
import csv
import io
import yaml
from eu.items import EuItem
from pathlib import Path


class EuSpider(scrapy.Spider):
    name = "eu_spider"
    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config_path = Path("/app/scraper.yaml")
        with open(config_path, "r", encoding="utf-8") as f:    

            self.config = yaml.safe_load(f)

    def start_requests(self):
        yield scrapy.Request(
            url=self.config["target_url"],
            callback=self.parse_csv,
            dont_filter=True
        )

    def parse_csv(self, response):
        reader = csv.DictReader(io.StringIO(response.text))

        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue

            yield EuItem(
                name=name,
                schema=row.get("schema", "").strip(),
                sanctions=row.get("sanctions", "").strip(),
                aliases=row.get("aliases", "").strip(),
            )
