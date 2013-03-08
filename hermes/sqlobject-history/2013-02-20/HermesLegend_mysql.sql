-- Exported definition from 2013-02-20T04:02:55
-- Class engines.HermesModels.HermesLegend
-- Database: mysql
CREATE TABLE hermes_legend (
    id INT PRIMARY KEY AUTO_INCREMENT,
    system_item_id INT(11),
    modified DATETIME,
    details TEXT,
    current BOOL,
    system_type_id INT
);
CREATE TABLE hermes_map_to_hermes_legend (
legend_id INT NOT NULL,
map_id INT NOT NULL
)

-- Constraints:
ALTER TABLE hermes_legend ADD CONSTRAINT hermes_legend_system_type_id_exists FOREIGN KEY (system_type_id) REFERENCES hermes_systems (id) 
