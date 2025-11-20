\copy table_name(column1, column2, column3) 
FROM '/path/to/file.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');
