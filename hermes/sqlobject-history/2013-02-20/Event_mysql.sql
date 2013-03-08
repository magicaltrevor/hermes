-- Exported definition from 2013-02-20T04:02:55
-- Class engines.Cron.Event
-- Database: mysql
CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    mins BLOB,
    hours BLOB,
    days BLOB,
    months BLOB,
    label VARCHAR(255),
    plugin VARCHAR(255),
    client VARCHAR(255),
    map INT,
    legend INT,
    params TINYBLOB,
    lastrun DATETIME
)
