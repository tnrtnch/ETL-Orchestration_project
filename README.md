# ETL Orchestration Project Summary<br />

Multi-Source Data Orchestration Pipeline<br />
Dockerized multi-source ETL orchestration pipeline using Apache Airflow, PostgreSQL, FastAPI, and Streamlit for sanctions intelligence and news aggregation.<br />
Overview<br />
This project is a Dockerized end-to-end data orchestration pipeline that:<br />
•	Scrapes data from multiple external sources<br />
•	Orchestrates workflows with Apache Airflow<br />
•	Merges and deduplicates datasets<br />
•	Stores structured data in PostgreSQL<br />
•	Exposes APIs through FastAPI<br />
•	Visualizes results with Streamlit<br />
The system demonstrates a complete modern ETL/ELT architecture for sanctions intelligence and news aggregation.<br />



# Architecture<br />
External Sources<br />
    ↓<br />
Scrapers / Crawlers<br />
    ↓<br />
Airflow DAG Orchestration<br />
    ↓<br />
Merge + Dedup Pipeline<br />
    ↓<br />
PostgreSQL<br />
    ↓<br />
FastAPI<br />
    ↓<br />
Streamlit Dashboard<br />



Tech Stack<br />
Layer	Technology<br />
Orchestration	Apache Airflow<br />
Backend API	FastAPI<br />
Database	PostgreSQL<br />
Dashboard	Streamlit<br />
Containerization	Docker Compose<br />
Data Processing	Python<br />
Scheduling	Airflow Scheduler<br />

	

Running Docker desktop images<br />
 


Data Sources<br />
1. EU FSF Sanctions<br />
Structured sanctions dataset.<br />
Output:<br />
/data/eu_fsf_sanctions.json<br />
Approximate records:<br />
~5900+<br />


2. INEGI Scraper<br />
Custom scraper for sanctioned providers.<br />
Outputs:<br />
/data/inegi_scraper.json<br />
/data/inegi_playwright.json<br />
Approximate records:<br />
75 + 75<br />



3. Kaldata News<br />
SQLite-based news ingestion.<br />
Output:<br />
/data/kaldata.db<br />


4. Telegraph News<br />
SQLite-based news ingestion.<br />
Output:<br />
/data/telegraph.db<br />


Airflow Orchestration<br />
DAGs<br />
DAG	Purpose<br />
EU FSF DAG	Downloads sanctions data<br />
INEGI DAG	Scrapes sanctioned providers<br />
Kaldata DAG	Collects news data<br />
Telegraph DAG	Collects news data<br />
Merge DAG	Merges and stores all outputs<br />
Merge Pipeline<br />
The merge pipeline:<br />
•	Reads all JSON and SQLite outputs<br />
•	Normalizes records<br />
•	Deduplicates entries<br />
•	Classifies data types<br />
•	Saves structured data into PostgreSQL<br />
Classification logic:<br />
Data Type	Target Table<br />
Sanctions	sanctions<br />
News	news<br />
Unknown/Other	raw_data<br />


PostgreSQL Schema<br />
sanctions<br />
Stores sanctions-related entities.<br />
Columns:<br />
•	id<br />
•	name<br />
•	source<br />
•	extra (JSONB)<br />
•	unique_key<br />


news<br />
Stores news articles.<br />
Columns:<br />
•	id<br />
•	title<br />
•	body<br />
•	author<br />
•	url<br />
•	source<br />



raw_data<br />
Fallback storage for unclassified records.<br />
Columns:<br />
•	id<br />
•	data (JSONB)<br />
•	source<br />
•	unique_key<br />

PostgreSQL counts<br />
 
Deduplication<br />
Deduplication is implemented using:<br />
UNIQUE CONSTRAINTS<br />
and:<br />
ON CONFLICT DO NOTHING<br />
This prevents uncontrolled duplicate growth across DAG reruns.<br />

Current Dataset Status<br />
Table	ApproximateRecords<br />
sanctions	6000+<br />
news	700+<br />
raw_data	minimal<br />


Localhost:8080<br />
 

Streamlit Dashboard<br />
The Streamlit dashboard provides:<br />
•	PostgreSQL integration<br />
•	Data table visualization<br />
•	Sanctions overview<br />
•	News overview<br />
•	Raw data inspection<br />
Potential future improvements:<br />
•	Search<br />
•	Filters<br />
•	Charts<br />
•	Analytics<br />
•	Entity exploration<br />
•	Monitoring metrics<br />



Streamlit localhost:8501<br />

 

API Layer<br />
FastAPI exposes REST endpoints:<br />
Endpoint	Purpose<br />
/sanctions	Retrieve sanctions<br />
/news	Retrieve news<br />
/raw	Retrieve fallback raw data<br />

FastAPI   http://localhost:8000/news<br />
 

Dockerized Infrastructure<br />
All services run through Docker Compose.<br />
Services:<br />
•	airflow-webserver<br />
•	airflow-scheduler<br />
•	postgres<br />
•	fastapi<br />
•	streamlit<br />
Shared volumes are used for:<br />
/data<br />
/logs<br />
/dags<br />


Docker Desktop<br />
 
Key Engineering Challenges Solved<br />
Shared Volume Consistency<br />
Unified all containers to use:<br />
/opt/airflow/data<br />
preventing stale outputs and path mismatches.<br />


Deduplication Stability<br />
Implemented unique keys and PostgreSQL constraints to stabilize repeated DAG executions.<br />



Classification Pipeline<br />
Improved sanctions classification logic to correctly ingest EU sanctions datasets.<br />

End-to-End Orchestration<br />
Validated complete orchestration flow:<br />
Scraper → Airflow → Merge → PostgreSQL → API → Dashboard<br />


Result<br />
The project demonstrates a fully operational orchestration pipeline capable of:<br />
•	Multi-source data ingestion<br />
•	Workflow orchestration<br />
•	Data normalization<br />
•	Deduplication<br />
•	Persistent storage<br />
•	API exposure<br />
•	Dashboard visualization<br />
This architecture can be extended toward:<br />
•	Intelligence platforms<br />
•	Compliance monitoring<br />
•	Entity resolution systems<br />
•	Real-time alerting<br />
•	Analytics dashboards<br />
•	Search and vector retrieval systems<br />

