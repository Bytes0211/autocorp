\copy auto_parts(sku, , column3) 
FROM '/path/to/file.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');
