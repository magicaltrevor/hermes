SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `hermes` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `hermes`;

-- -----------------------------------------------------
-- Table `hermes`.`jobs`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hermes`.`jobs` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `plugin` VARCHAR(45) NULL ,
  `to_address` VARCHAR(255) NULL ,
  `from_address` VARCHAR(255) NULL ,
  `subject` VARCHAR(255) NULL ,
  `message` VARCHAR(40000) NULL ,
  `created_at` DATETIME NULL ,
  `login` VARCHAR(255) NULL ,
  `password` VARCHAR(255) NULL ,
  `times_processed` INT(3) DEFAULT 0,
  `info` VARCHAR(255) NULL,
  `priority` INT(1) DEFAULT 5,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;

CREATE INDEX job_by_id ON `hermes`.`jobs` (`id` ASC, `message` ASC) ;

CREATE INDEX job_by_date USING BTREE ON `hermes`.`jobs` (`created_at` ASC, `message` ASC) ;

CREATE INDEX date ON `hermes`.`jobs` (`created_at` ASC) ;

CREATE INDEX index_to ON `hermes`.`jobs` (`to_address` ASC) ;

CREATE INDEX index_priority ON `hermes`.`jobs` (`priority` ASC) ;

-- -----------------------------------------------------
-- Table `hermes`.`in_process`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hermes`.`in_process` (
  `id` INT NOT NULL ,
  `plugin` VARCHAR(45) NULL ,
  `to_address` VARCHAR(255) NULL ,
  `from_address` VARCHAR(255) NULL ,
  `subject` VARCHAR(255) NULL ,
  `message` VARCHAR(40000) NULL ,
  `pickedup_at` DATETIME NULL ,
  `login` VARCHAR(255) NULL ,
  `password` VARCHAR(255) NULL ,
  `times_processed` INT(3) DEFAULT 0,
  `info` VARCHAR(255) NULL,
  `priority` INT(1) DEFAULT 5,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_in_process_jobs`
    FOREIGN KEY (`id` )
    REFERENCES `hermes`.`jobs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX fk_in_process_jobs ON `hermes`.`in_process` (`id` ASC) ;

CREATE INDEX in_process_by_id ON `hermes`.`in_process` (`id` ASC, `message` ASC) ;

CREATE INDEX in_process_by_date USING BTREE ON `hermes`.`in_process` (`pickedup_at` ASC, `message` ASC) ;

CREATE INDEX date ON `hermes`.`in_process` (`pickedup_at` ASC) ;

CREATE INDEX index_to ON `hermes`.`in_process` (`to_address` ASC) ;

CREATE INDEX index_priority ON `hermes`.`in_process` (`priority` ASC) ;


-- -----------------------------------------------------
-- Table `hermes`.`completed`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hermes`.`completed` (
  `id` INT NOT NULL ,
  `plugin` VARCHAR(45) NULL ,
  `to_address` VARCHAR(255) NULL ,
  `from_address` VARCHAR(255) NULL ,
  `subject` VARCHAR(255) NULL ,
  `message` VARCHAR(40000) NULL ,
  `completed_at` DATETIME NULL ,
  `login` VARCHAR(255) NULL ,
  `password` VARCHAR(255) NULL ,
  `times_processed` INT(3) DEFAULT 0,
  `info` VARCHAR(255) NULL,
  `priority` INT(1) DEFAULT 5,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_completed_jobs`
    FOREIGN KEY (`id` )
    REFERENCES `hermes`.`jobs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX fk_completed_jobs ON `hermes`.`completed` (`id` ASC) ;

CREATE INDEX completed_by_id ON `hermes`.`completed` (`id` ASC, `message` ASC) ;

CREATE INDEX completed_by_date USING BTREE ON `hermes`.`completed` (`completed_at` ASC, `message` ASC) ;

CREATE INDEX date USING BTREE ON `hermes`.`completed` (`completed_at` ASC) ;

CREATE INDEX index_to ON `hermes`.`completed` (`to_address` ASC) ;

CREATE INDEX index_priority ON `hermes`.`completed` (`priority` ASC) ;

-- -----------------------------------------------------
-- Table `hermes`.`failed`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hermes`.`failed` (
  `id` INT NOT NULL ,
  `plugin` VARCHAR(45) NULL ,
  `to_address` VARCHAR(255) NULL ,
  `from_address` VARCHAR(255) NULL ,
  `subject` VARCHAR(255) NULL ,
  `message` VARCHAR(40000) NULL ,
  `failed_at` DATETIME NULL ,
  `login` VARCHAR(255) NULL ,
  `password` VARCHAR(255) NULL ,
  `times_processed` INT(3) DEFAULT 0,
  `info` VARCHAR(255) NULL,
  `priority` INT(1) DEFAULT 5,
  PRIMARY KEY (`id`) ,
  CONSTRAINT `fk_failed_jobs`
    FOREIGN KEY (`id` )
    REFERENCES `hermes`.`jobs` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX fk_failed_jobs ON `hermes`.`failed` (`id` ASC) ;

CREATE INDEX failed_by_id ON `hermes`.`failed` (`id` ASC, `message` ASC) ;

CREATE INDEX failed_by_date USING BTREE ON `hermes`.`failed` (`failed_at` ASC, `message` ASC) ;

CREATE INDEX date ON `hermes`.`failed` (`failed_at` ASC) ;

CREATE INDEX index_to ON `hermes`.`failed` (`to_address` ASC) ;

CREATE INDEX index_priority ON `hermes`.`failed` (`priority` ASC) ;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
