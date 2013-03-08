-- Exported definition from 2013-02-20T04:02:55
-- Class engines.HermesModels.DataStore
-- Database: mysql
CREATE TABLE hermes_datastore (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_id INT(11),
    file_system_id INT,
    data_type VARCHAR(255),
    map_id INT,
    created_at DATETIME,
    modified_at DATETIME,
    deleted_at DATETIME,
    raw_data MEDIUMBLOB
);
CREATE TABLE hermes_datastore_relationships (
from_id INT NOT NULL,
to_id INT NOT NULL
)

-- Constraints:
ALTER TABLE hermes_datastore ADD CONSTRAINT hermes_datastore_file_system_id_exists FOREIGN KEY (file_system_id) REFERENCES hermes_systems (id) 
ALTER TABLE hermes_datastore ADD CONSTRAINT hermes_datastore_map_id_exists FOREIGN KEY (map_id) REFERENCES hermes_map (id) 
