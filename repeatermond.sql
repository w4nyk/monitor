-- phpMyAdmin SQL Dump
-- version 4.6.6deb4
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 17, 2018 at 12:53 PM
-- Server version: 10.1.23-MariaDB-9+deb9u1
-- PHP Version: 7.0.30-0+deb9u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `w4nykMonitor`
--
CREATE DATABASE IF NOT EXISTS `w4nykMonitor` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `w4nykMonitor`;

-- --------------------------------------------------------

--
-- Table structure for table `analogInput`
--

DROP TABLE IF EXISTS `analogInput`;
CREATE TABLE `analogInput` (
  `id` int(11) NOT NULL,
  `unix_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `analog0` decimal(10,3) DEFAULT NULL COMMENT '450ft forward',
  `analog1` decimal(10,3) DEFAULT NULL COMMENT '450ft reverse',
  `analog2` decimal(10,3) DEFAULT NULL COMMENT '300ft forward',
  `analog3` decimal(10,3) DEFAULT NULL COMMENT '300ft reverse',
  `analog4` decimal(10,3) DEFAULT NULL COMMENT '200ft forward',
  `analog5` decimal(10,3) DEFAULT NULL COMMENT '200ft reverse',
  `analog6` decimal(10,3) DEFAULT NULL COMMENT '100ft forward',
  `analog7` decimal(10,3) DEFAULT NULL COMMENT '100ft reverse',
  `analog8` decimal(10,3) DEFAULT NULL COMMENT 'adref'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Analog Input voltages';

-- --------------------------------------------------------

--
-- Table structure for table `calibration`
--

DROP TABLE IF EXISTS `calibration`;
CREATE TABLE `calibration` (
  `id` int(11) NOT NULL,
  `unix_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `elementSize` int(11) NOT NULL,
  `fiveW` float(10,3) NOT NULL,
  `tenW` float(10,3) NOT NULL,
  `fifteenW` float(10,3) NOT NULL,
  `twentyW` float(10,3) NOT NULL,
  `twentyfiveW` float(10,3) NOT NULL,
  `thirtyW` float(10,3) NOT NULL,
  `thirtyfiveW` float(10,3) NOT NULL,
  `fortyW` float(10,3) NOT NULL,
  `fortyfiveW` float(10,3) NOT NULL,
  `fiftyW` float(10,3) NOT NULL,
  `fiftyfiveW` float(10,3) NOT NULL,
  `sixtyW` float(10,3) NOT NULL,
  `sixtyfiveW` float(10,3) NOT NULL,
  `seventyW` float(10,3) NOT NULL,
  `seventyfiveW` float(10,3) NOT NULL,
  `eightyW` float(10,3) NOT NULL,
  `eightyfiveW` float(10,3) NOT NULL,
  `ninetyW` float(10,3) NOT NULL,
  `ninetyfiveW` float(10,3) NOT NULL,
  `onehundredW` float(10,3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Holds wattmeter element calibration values';

-- --------------------------------------------------------

--
-- Table structure for table `digInput`
--

DROP TABLE IF EXISTS `digInput`;
CREATE TABLE `digInput` (
  `id` int(11) NOT NULL,
  `unix_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dig0` tinyint(1) NOT NULL COMMENT 'xmit trigger repeater0',
  `dig1` tinyint(1) NOT NULL,
  `dig2` tinyint(1) NOT NULL,
  `dig3` tinyint(1) NOT NULL,
  `dig4` tinyint(1) NOT NULL,
  `dig5` tinyint(1) NOT NULL,
  `dig6` tinyint(1) NOT NULL,
  `dig7` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Digital input status';

-- --------------------------------------------------------

--
-- Table structure for table `swr`
--

DROP TABLE IF EXISTS `swr`;
CREATE TABLE `swr` (
  `id` int(11) NOT NULL,
  `unix_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fourfifty` decimal(10,3) DEFAULT NULL COMMENT '450ft swr',
  `threeHundred` decimal(10,3) DEFAULT NULL COMMENT '300ft swr',
  `twoHundred` decimal(10,3) DEFAULT NULL COMMENT '200ft swr',
  `oneHundred` decimal(10,3) DEFAULT NULL COMMENT '100ft swr'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `analogInput`
--
ALTER TABLE `analogInput`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `calibration`
--
ALTER TABLE `calibration`
  ADD PRIMARY KEY (`id`),
  ADD KEY `elementSize` (`elementSize`);

--
-- Indexes for table `digInput`
--
ALTER TABLE `digInput`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `swr`
--
ALTER TABLE `swr`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `analogInput`
--
ALTER TABLE `analogInput`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `calibration`
--
ALTER TABLE `calibration`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `digInput`
--
ALTER TABLE `digInput`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `swr`
--
ALTER TABLE `swr`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
