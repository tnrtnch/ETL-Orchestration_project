from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://airflow:airflow@postgres:5432/airflow"
)


@app.get("/")
def root():
    return {"message": "API is running."}


@app.get("/news")
def get_news():

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT title, source
        FROM news
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


@app.get("/sanctions")
def get_sanctions():

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, source
        FROM sanctions
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


@app.get("/raw")
def get_raw():

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT data, source
        FROM raw_data
    """)

    rows = cur.fetchall()

    result = []

    for row in rows:
        result.append({
            "data": row[0],
            "source": row[1]
        })

    cur.close()
    conn.close()

    return result