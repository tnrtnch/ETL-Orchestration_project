## Automation (GitHub Actions – External Scheduler)

This repository is designed to run **as a worker**, triggered by an external GitHub Actions scheduler.

It does **not** rely on its own `schedule` event.

Instead, execution is initiated via a dedicated **cron trigger repository** using the GitHub `repository_dispatch` mechanism.

---

### How Automation Works

Typical execution flow:

1. **Cron Trigger Repository**
   - Runs on a scheduled GitHub Actions workflow (hourly / daily)
   - Sends a `repository_dispatch` event

2. **This Worker Repository**
   - Receives the dispatch event
   - Runs the Scrapy spider
   - Validates and processes EU FSF sanctions data
   - Generates `eu_fsf_sanctions.json`
   - Commits and pushes the updated JSON file automatically

---

### Why This Architecture?

This split architecture is intentional and provides:

- Reliable scheduling (avoids GitHub Actions `schedule` inconsistencies)
- Clear separation of responsibilities
- Easier debugging and monitoring
- Production-grade automation pattern

---

### Trigger Types Supported

- `repository_dispatch` (primary, automated)
- `workflow_dispatch` (manual runs for testing)

---

### Notes

- This repository **must have write permissions** enabled for GitHub Actions
- JSON output is force-updated on every run
- No CSV files are persisted — CSV is used only as an in-memory source



---

## Features

* Downloads the latest EU sanctions dataset from a configurable source
* Reads CSV **in-memory only** (no temporary CSV files written to disk)
* Validates CSV schema before processing
* Extracts and normalizes:

  * `name`
  * `schema`
  * `sanctions`
  * `aliases`
* Handles missing values safely (no `NaN` in outputs)
* Exports a single clean **JSON file** via Scrapy Item Pipelines
* Configurable via `scraper.yaml`
* Production-ready structure (Scrapy architecture preserved)

---

## Project Structure

```
eu_fsf_sanc/
├── eu/
│   ├── spiders/
│   │   └── eu_spider.py        # Main spide
│   ├── pipelines.py            # JSON output pipeline
│   ├── validators.py           # CSV schema validation
│   ├── middlewares.py  
│   ├── items.py                # Item definitions
│   └── settings.py
├── eu_fsf_sanctions.json       # outpu file
├── scraper.yaml                # Configuration file
├── scrapy.cfg
├── requirements.txt
└── README.md
```
---


## Configuration (`scraper.yaml`)

```yaml
target_url: https://data.opensanctions.org/datasets/latest/eu_fsf/targets.simple.csv
output_file: sanctions.json
```

### Configuration Notes

* `output_file` is optional
* If omitted, the default output will be:

```text
sanctions.json
```

---

## How It Works

1. **Spider starts** (`eu_spider`)
2. CSV file is downloaded via HTTP
3. CSV content is read into memory
4. Schema is validated (`validators.py`)
5. Rows are converted into `EuItem`
6. Items are written to JSON by the pipeline
7. Spider exits cleanly

No CSV file is saved to disk at any stage.

---

## Running the Spider

```bash
scrapy crawl eu_spider
```

The output JSON file will be created in the same directory as `items.py` and `pipelines.py`.

---

## Output Example (`sanctions.json`)

```json
[
  {
    "name": "Tamam Raad",
    "schema": "Person",
    "sanctions": "SYR - 2024/1517 (OJ L28052024) - 2020-10-16",
    "aliases": "Tamam RA’AD;Tammam RA’AD;Tammam Raad;تمام رعد"
  }
]
```

* Empty aliases are written as empty strings (`""`)
* No `null` or `NaN` values

---

## CSV Schema Validation

The pipeline ensures required columns exist before processing.

If validation fails:

* The spider stops
* A clear error is logged

This prevents silent data corruption.

---

## Automation (GitHub Actions Ready)

This project is suitable for:

* Triggered by an external scheduler repository
* Automatic commits of updated JSON files
* CI/CD pipelines

Typical setup:

* `cron` trigger (daily)
* Run spider
* Commit updated `sanctions.json`

---

## Design Principles

* No Selenium / browser automation
* No filesystem pollution
* Deterministic output
* Clear separation of concerns
* Scrapy-native architecture

---

## Mail alert

Failure notifications are automatically sent via email using GitHub Actions.
---


## License

This project is provided for educational and research purposes.
Please verify data usage rights with the original data provider.

---

## Contributions

Pull requests and improvements are welcome.

---

