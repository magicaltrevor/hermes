-- Exported definition from 2013-02-20T04:02:55
-- Class engines.HermesModels.HermesMap
-- Database: mysql
CREATE TABLE hermes_map (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    modified DATETIME,
    details TEXT,
    status VARCHAR(20),
    type VARCHAR(30),
    current BOOL,
    system_type_id INT
)

-- Constraints:
ALTER TABLE hermes_map ADD CONSTRAINT hermes_map_system_type_id_exists FOREIGN KEY (system_type_id) REFERENCES hermes_systems (id) 
