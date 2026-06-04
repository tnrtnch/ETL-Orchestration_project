CREATE TABLE IF NOT EXISTS sanctions (
    id SERIAL PRIMARY KEY,
    name TEXT,
    source TEXT,
    extra JSONB,
    unique_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title TEXT,
    url TEXT UNIQUE,
    body TEXT,
    author TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS raw_data (
    id SERIAL PRIMARY KEY,
    data JSONB,
    source TEXT
);