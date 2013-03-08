-- Exported definition from 2013-02-20T04:02:55
-- Class engines.HermesModels.DataStoreImported
-- Database: mysql
CREATE TABLE hermes_datastore_imported (
    id INT PRIMARY KEY AUTO_INCREMENT,
    datastore_id INT,
    system_item_id INT(11) NOT NULL,
    system_id INT,
    imported_at DATETIME
)

-- Constraints:
ALTER TABLE hermes_datastore_imported ADD CONSTRAINT hermes_datastore_imported_datastore_id_exists FOREIGN KEY (datastore_id) REFERENCES hermes_datastore (id) ON DELETE CASCADE
ALTER TABLE hermes_datastore_imported ADD CONSTRAINT hermes_datastore_imported_system_id_exists FOREIGN KEY (system_id) REFERENCES hermes_systems (id) 
