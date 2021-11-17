CREATE TABLE IF NOT EXISTS catalog_table (
    id VARCHAR(400) NOT NULL,
    title VARCHAR(400)NOT NULL,
    link VARCHAR(400) NOT NULL,
    image VARCHAR(400),
    price FLOAT(3) NOT NULL,
    discount INT,
    price_tag VARCHAR(400),
    review_rate FLOAT(3),
    review_count INT,
    search_id INT,
    
    FOREIGN KEY (search_id)
    REFERENCES search_table (id)
);

