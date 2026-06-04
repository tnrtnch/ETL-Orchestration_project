import streamlit as st
import pandas as pd
import psycopg2

DB_URL = "postgresql://airflow:airflow@postgres:5432/airflow"

st.set_page_config(page_title="Sanctions Dashboard", layout="wide")

st.title("Sanctions Dashboard")

conn = psycopg2.connect(DB_URL)



# COUNTS

sanctions_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM sanctions",
    conn
)

news_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM news",
    conn
)

raw_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM raw_data",
    conn
)

col1, col2, col3 = st.columns(3)

col1.metric("Sanctions", sanctions_count["count"][0])
col2.metric("News", news_count["count"][0])
col3.metric("Raw Data", raw_count["count"][0])



# SANCTIONS BY SOURCE

st.subheader("Sanctions by Source")

sanctions_by_source = pd.read_sql(
    """
    SELECT source, COUNT(*) as count
    FROM sanctions
    GROUP BY source
    ORDER BY count DESC
    """,
    conn
)

st.dataframe(sanctions_by_source)

st.bar_chart(
    sanctions_by_source.set_index("source")
)



# NEWS TABLE

st.subheader("Latest News")

news_df = pd.read_sql(
    """
    SELECT title, source
    FROM news
    """,
    conn
)

st.dataframe(news_df)



# RAW TABLE

st.subheader("Raw data")

raw_df = pd.read_sql(
    """
    SELECT
        source,
        data::text
    FROM raw_data
    """,
    conn
)

st.dataframe(raw_df)

conn.close()