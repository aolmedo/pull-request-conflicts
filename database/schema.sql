CREATE TABLE IF NOT EXISTS `broadleaf_pull_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `head_repo_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_repo_id` INT(11) NOT NULL COMMENT '',
  `head_commit_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_commit_id` INT(11) NOT NULL COMMENT '',
  `pullreq_id` INT(11) NOT NULL COMMENT '',
  `intra_branch` TINYINT(1) NOT NULL COMMENT '',
  `merged` TINYINT(1) NOT NULL COMMENT '',
  `opened_at` TIMESTAMP COMMENT '',
  `closed_at` TIMESTAMP COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `twitter4j_pull_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `head_repo_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_repo_id` INT(11) NOT NULL COMMENT '',
  `head_commit_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_commit_id` INT(11) NOT NULL COMMENT '',
  `pullreq_id` INT(11) NOT NULL COMMENT '',
  `intra_branch` TINYINT(1) NOT NULL COMMENT '',
  `merged` TINYINT(1) NOT NULL COMMENT '',
  `opened_at` TIMESTAMP COMMENT '',
  `closed_at` TIMESTAMP COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `antlr4_pull_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `head_repo_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_repo_id` INT(11) NOT NULL COMMENT '',
  `head_commit_id` INT(11) NULL DEFAULT NULL COMMENT '',
  `base_commit_id` INT(11) NOT NULL COMMENT '',
  `pullreq_id` INT(11) NOT NULL COMMENT '',
  `intra_branch` TINYINT(1) NOT NULL COMMENT '',
  `merged` TINYINT(1) NOT NULL COMMENT '',
  `opened_at` TIMESTAMP COMMENT '',
  `closed_at` TIMESTAMP COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;
