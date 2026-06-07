from datetime import datetime

import json
import os


class InegiPipeline:
    def open_spider(self, spider):
        self.data = []
        spider.logger.info("Pipeline started")

    def process_item(self, item, spider):
        self.data.append(dict(item)) 
        return item

    def close_spider(self, spider):  
        spider.logger.info("Removing duplicate name entries...")
        
        merged_data = {}
        for entry in self.data:
            name = entry.get("name")
            numbers = entry.get("sanction_numbers") or []

            if not name:
                 continue
            
            name = name.strip().upper()
            
            if not isinstance(numbers, list):
                 numbers = [numbers]

            numbers = [n for n in numbers if n]

            # Remove duplicate names and numbers
            if name not in merged_data:
                    merged_data[name] = set(numbers)
            else:
                    merged_data[name].update(numbers)

        cleaned_data = []

        for name, numbers in merged_data.items():
            cleaned_data.append({
                "name": name,
                "sanction_numbers": sorted(list(numbers)),
                "origin": "inegi_scraper"
            })

        
        output_file = spider.config.get("output_file", "inegi_scraper.json")
        output_path = os.path.abspath(output_file)

        utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        output_data = {
            "last_updated": utc_time,
            "data": cleaned_data,   
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        spider.logger.info(f"{len(cleaned_data)} profile(s) saved: {output_path}")