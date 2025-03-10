-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables if they exist
DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `issues`;
DROP TABLE IF EXISTS `users`;

-- Enable foreign key checks   
SET FOREIGN_KEY_CHECKS = 1;

-- Create users table
CREATE TABLE `users`(
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(20) NOT NULL,
    `password_hash` CHAR(60) BINARY NOT NULL COMMENT 'Bcrypt Password Hash and Salt (60 bytes)', 
    `email` VARCHAR(320) NOT NULL,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `location` VARCHAR(50) NOT NULL,
    `profile_image` VARCHAR(255),
    `role` ENUM('visitor', 'helper', 'admin') NOT NULL,
	`status` ENUM('active', 'inactive') NOT NULL,
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `username` (`username`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- Create issues table
CREATE TABLE `issues` (
    `issue_id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `summary` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('new', 'open', 'stalled', 'resolved') NOT NULL DEFAULT 'new',
    PRIMARY KEY (`issue_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- Create comments table
CREATE TABLE `comments` (
  `comment_id` INT NOT NULL AUTO_INCREMENT,
  `issue_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  FOREIGN KEY (`issue_id`) REFERENCES `issues`(`issue_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;