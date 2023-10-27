CREATE TABLE etl_log (
    log_id INT IDENTITY PRIMARY KEY,
    process_name VARCHAR(255) NOT NULL,
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    source_table_name VARCHAR(255) NOT NULL,
    target_table_name VARCHAR(255) NOT NULL,
    record_count INT,
    error_message TEXT,
    duration_in_seconds INT,
    source_system VARCHAR(50), 
	source_type VARCHAR(50), 
    target_system VARCHAR(50),
	target_type VARCHAR(50),
    source_file_path VARCHAR(255),
    target_file_path VARCHAR(255),
    etl_type VARCHAR(20), 
    memory_occupied BIGINT,  
	additional_info TEXT
);

