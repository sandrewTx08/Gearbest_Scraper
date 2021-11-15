CREATE TABLE IF NOT EXISTS catalog_table (
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    image TEXT,
    price REAL NOT NULL,
    discount INTEGER,
    price_tag TEXT,
    review_rate REAL,
    review_count INTEGER,
    search_id INTEGER,
    FOREIGN KEY (search_id)
    REFERENCES search_table (id)
);

