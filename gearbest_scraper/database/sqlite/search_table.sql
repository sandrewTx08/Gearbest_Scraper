CREATE TABLE IF NOT EXISTS search_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT,
    category TEXT,
    pages_count INTEGER,
    datetime TEXT,
    currency_id TEXT,

    FOREIGN KEY (currency_id)
    REFERENCES currency_table (id)
);

