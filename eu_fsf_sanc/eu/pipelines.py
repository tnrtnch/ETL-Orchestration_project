import json
from eu.validators import validate_item
from pathlib import Path
from datetime import datetime

class EuPipeline:
    def open_spider(self, spider):
        self.items = []
        # self.base_dir = Path(__file__).resolve().parent
  
        output_file = spider.config.get("output_file")
        # self.json_path = self.base_dir / output_file
        self.json_path = Path(output_file)

    def process_item(self, item, spider):
        item = validate_item(item)
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        output = {
            "generated_at": datetime.utcnow().isoformat(),
            "items": self.items
        }
        
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=2
            )

        spider.logger.info(
            f"{len(self.items)} records written to {self.json_path}"
        )
