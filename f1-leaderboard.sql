-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Oct 28, 2025 at 12:54 PM
-- Server version: 8.3.0
-- PHP Version: 8.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `f1-leaderboard`
--

-- --------------------------------------------------------

--
-- Table structure for table `cars`
--

DROP TABLE IF EXISTS `cars`;
CREATE TABLE IF NOT EXISTS `cars` (
                                      `car_id` int NOT NULL AUTO_INCREMENT,
                                      `name` varchar(255) NOT NULL,
    PRIMARY KEY (`car_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `laptimes`
--

DROP TABLE IF EXISTS `laptimes`;
CREATE TABLE IF NOT EXISTS `laptimes` (
                                          `laptimes_id` int NOT NULL AUTO_INCREMENT,
                                          `user_id` int NOT NULL,
                                          `track_id` int NOT NULL,
                                          `car_id` int NOT NULL,
                                          `session_id` int NOT NULL,
                                          `laptime` int NOT NULL,
                                          `sector1` int NOT NULL,
                                          `sector2` int NOT NULL,
                                          `sector3` int NOT NULL,
                                          `is_valid` tinyint(1) NOT NULL,
    `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`laptimes_id`),
    KEY `user_id` (`user_id`),
    KEY `track_id` (`track_id`),
    KEY `car_id` (`car_id`),
    KEY `session_id` (`session_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
CREATE TABLE IF NOT EXISTS `sessions` (
                                          `session_id` int NOT NULL AUTO_INCREMENT,
                                          `user_id` int NOT NULL,
                                          `car_id` int NOT NULL,
                                          `start_time` datetime NOT NULL,
                                          `end_time` datetime NOT NULL,
                                          PRIMARY KEY (`session_id`),
    KEY `user_id` (`user_id`),
    KEY `car_id` (`car_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `track`
--

DROP TABLE IF EXISTS `track`;
CREATE TABLE IF NOT EXISTS `track` (
                                       `track_id` int NOT NULL AUTO_INCREMENT,
                                       `name` varchar(255) NOT NULL,
    `location` varchar(255) NOT NULL,
    PRIMARY KEY (`track_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
                                       `user_id` int NOT NULL AUTO_INCREMENT,
                                       `username` varchar(50) NOT NULL,
    `student_number` int NOT NULL,
    `password_hash` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `student_number` (`student_number`),
    UNIQUE KEY `username` (`username`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `laptimes`
--
ALTER TABLE `laptimes`
    ADD CONSTRAINT `laptimes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `laptimes_ibfk_2` FOREIGN KEY (`track_id`) REFERENCES `track` (`track_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `laptimes_ibfk_3` FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `laptimes_ibfk_4` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`session_id`) ON DELETE CASCADE;

--
-- Constraints for table `sessions`
--
ALTER TABLE `sessions`
    ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `sessions_ibfk_2` FOREIGN KEY (`car_id`) REFERENCES `cars` (`car_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
