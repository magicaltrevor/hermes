-- Exported definition from 2013-02-20T04:04:13
-- Class engines.HermesModels.HermesSystems
-- Database: mysql
CREATE TABLE hermes_systems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    short_name VARCHAR(20),
    name VARCHAR(20),
    meta TEXT,
    modified DATETIME,
    status VARCHAR(20)
)
