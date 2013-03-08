-- Exported definition from 2013-02-20T04:02:55
-- Class engines.HermesModels.StoreAttributes
-- Database: mysql
CREATE TABLE hermes_datastore_attributes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    datastore_id INT,
    field_name VARCHAR(255),
    field_value TEXT,
    data_type VARCHAR(255),
    created_at DATETIME,
    modified_at DATETIME,
    deleted_at DATETIME
)

-- Constraints:
ALTER TABLE hermes_datastore_attributes ADD CONSTRAINT hermes_datastore_attributes_datastore_id_exists FOREIGN KEY (datastore_id) REFERENCES hermes_datastore (id) ON DELETE CASCADE
