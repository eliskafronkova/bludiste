-- phpMyAdmin SQL Dump
 -- version 5.2.1
 -- https://www.phpmyadmin.net/
 --
 -- Počítač: localhost
 -- Vytvořeno: Ned 08. pro 2024, 12:29
 -- Verze serveru: 10.5.25-MariaDB
 -- Verze PHP: 8.2.25
 
 SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
 START TRANSACTION;
 SET time_zone = "+00:00";
 
 
 /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
 /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
 /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 /*!40101 SET NAMES utf8mb4 */;
 
 --
 -- Databáze: `vyuka10`
 --
 
 -- --------------------------------------------------------
 
 --
 -- Struktura tabulky `UsersMaze`
 --
 
 CREATE TABLE `UsersMaze` (
   `ID` bigint(20) NOT NULL,
   `Username` varchar(128) NOT NULL,
   `Password` varchar(128) NOT NULL
   `Password` varchar(128) NOT NULL,
   `Admin` bit (1) NOT NULL DEFAULT b'0'
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
 
 --
 -- Indexy pro exportované tabulky
 --
 
 --
 -- Indexy pro tabulku `UsersMaze`
 --
 ALTER TABLE `UsersMaze`
   ADD PRIMARY KEY (`ID`);
 
 --
 -- AUTO_INCREMENT pro tabulky
 --
 
 --
 -- AUTO_INCREMENT pro tabulku `UsersMaze`
 --
 ALTER TABLE `UsersMaze`
   MODIFY `ID` bigint(20) NOT NULL AUTO_INCREMENT;
 COMMIT;
 
 /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
 /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
 /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;