CREATE TABLE IF NOT EXISTS search_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(400),
    category VARCHAR(400),
    pages_count INT,
    datetime VARCHAR(400),
    currency_id INT,
    
    FOREIGN KEY (currency_id)
    REFERENCES currency_table (id)
);

