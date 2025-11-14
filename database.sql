-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Gegenereerd op: 14 nov 2025 om 10:23
-- Serverversie: 8.3.0
-- PHP-versie: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `racesimulator`
--

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `drivers`
--

DROP TABLE IF EXISTS `drivers`;
CREATE TABLE IF NOT EXISTS `drivers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `car_index` tinyint UNSIGNED NOT NULL,
  `driver_name` varchar(50) DEFAULT NULL,
  `team_id` tinyint UNSIGNED DEFAULT NULL,
  `race_number` tinyint UNSIGNED DEFAULT NULL,
  `nationality` tinyint UNSIGNED DEFAULT NULL,
  `is_player` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_driver` (`session_id`,`car_index`),
  KEY `idx_session_car` (`session_id`,`car_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `laps`
--

DROP TABLE IF EXISTS `laps`;
CREATE TABLE IF NOT EXISTS `laps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `car_index` tinyint UNSIGNED NOT NULL,
  `lap_number` tinyint UNSIGNED NOT NULL,
  `lap_time_ms` int UNSIGNED DEFAULT NULL,
  `sector1_ms` int UNSIGNED DEFAULT NULL,
  `sector2_ms` int UNSIGNED DEFAULT NULL,
  `sector3_ms` int UNSIGNED DEFAULT NULL,
  `sector1_valid` tinyint(1) DEFAULT '1',
  `sector2_valid` tinyint(1) DEFAULT '1',
  `sector3_valid` tinyint(1) DEFAULT '1',
  `is_valid` tinyint(1) DEFAULT '1',
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_lap` (`session_id`,`car_index`,`lap_number`),
  KEY `idx_session_valid` (`session_id`,`is_valid`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Gegevens worden geëxporteerd voor tabel `laps`
--

INSERT INTO `laps` (`id`, `session_id`, `car_index`, `lap_number`, `lap_time_ms`, `sector1_ms`, `sector2_ms`, `sector3_ms`, `sector1_valid`, `sector2_valid`, `sector3_valid`, `is_valid`, `recorded_at`) VALUES
(1, 3, 0, 2, 67734, 16851, 30073, 20810, 0, 0, 0, 0, '2025-11-11 12:41:54'),
(2, 3, 0, 1, 68228, 17049, 30353, 20825, 0, 0, 0, 0, '2025-11-11 12:41:54'),
(3, 3, 0, 3, 79621, 17314, 41663, 20642, 0, 0, 0, 0, '2025-11-11 12:41:54'),
(4, 3, 0, 4, 67044, 16327, 30138, 20578, 1, 1, 1, 1, '2025-11-11 12:41:54'),
(5, 3, 0, 5, 69141, 16981, 31326, 20832, 0, 0, 0, 0, '2025-11-11 12:45:12'),
(6, 3, 0, 6, 70289, 18128, 31144, 21016, 0, 1, 1, 1, '2025-11-11 12:46:23'),
(7, 3, 0, 7, 73594, 17485, 34996, 21112, 0, 0, 0, 0, '2025-11-11 12:47:36');

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `sessions`
--

DROP TABLE IF EXISTS `sessions`;
CREATE TABLE IF NOT EXISTS `sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_uid` bigint UNSIGNED NOT NULL,
  `track_id` tinyint UNSIGNED DEFAULT NULL,
  `session_type` tinyint UNSIGNED DEFAULT NULL,
  `weather` tinyint UNSIGNED DEFAULT NULL,
  `track_temperature` tinyint DEFAULT NULL,
  `air_temperature` tinyint DEFAULT NULL,
  `total_laps` tinyint UNSIGNED DEFAULT NULL,
  `session_duration` int UNSIGNED DEFAULT NULL,
  `started_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ended_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_uid` (`session_uid`),
  KEY `idx_session_uid` (`session_uid`),
  KEY `idx_started_at` (`started_at`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Gegevens worden geëxporteerd voor tabel `sessions`
--

INSERT INTO `sessions` (`id`, `session_uid`, `track_id`, `session_type`, `weather`, `track_temperature`, `air_temperature`, `total_laps`, `session_duration`, `started_at`, `ended_at`) VALUES
(1, 4404545446215209195, 17, 18, 0, 32, 22, 2, 600, '2025-11-11 08:38:22', NULL),
(2, 1886371530664575468, 17, 18, 0, 31, 21, 2, 600, '2025-11-11 10:06:56', NULL),
(3, 6679039456791228148, 0, 0, 0, 0, 0, 0, 0, '2025-11-11 12:39:37', NULL);

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `telemetry_live`
--

DROP TABLE IF EXISTS `telemetry_live`;
CREATE TABLE IF NOT EXISTS `telemetry_live` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `car_index` tinyint UNSIGNED NOT NULL,
  `speed` smallint UNSIGNED DEFAULT NULL,
  `throttle` float DEFAULT NULL,
  `brake` float DEFAULT NULL,
  `gear` tinyint DEFAULT NULL,
  `rpm` smallint UNSIGNED DEFAULT NULL,
  `drs` tinyint(1) DEFAULT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_car_time` (`session_id`,`car_index`,`recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Beperkingen voor geëxporteerde tabellen
--

--
-- Beperkingen voor tabel `drivers`
--
ALTER TABLE `drivers`
  ADD CONSTRAINT `drivers_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE;

--
-- Beperkingen voor tabel `laps`
--
ALTER TABLE `laps`
  ADD CONSTRAINT `laps_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE;

--
-- Beperkingen voor tabel `telemetry_live`
--
ALTER TABLE `telemetry_live`
  ADD CONSTRAINT `telemetry_live_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
