CREATE DATABASE  IF NOT EXISTS `FP_Info12025_2` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `FP_Info12025_2`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: FP_Info12025_2
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `daily_records`
--

DROP TABLE IF EXISTS `daily_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `date` date DEFAULT NULL,
  `sleep_hours` float DEFAULT NULL,
  `mood` int DEFAULT NULL,
  `physical_activity` varchar(255) DEFAULT NULL,
  `food` varchar(255) DEFAULT NULL,
  `symptoms` varchar(255) DEFAULT NULL,
  `blood_pressure` varchar(20) DEFAULT NULL,
  `glucose` float DEFAULT NULL,
  `bpm` int DEFAULT NULL,
  `weight` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `daily_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_records`
--

LOCK TABLES `daily_records` WRITE;
/*!40000 ALTER TABLE `daily_records` DISABLE KEYS */;
INSERT INTO `daily_records` VALUES (1,1,'2025-11-13',6.5,5,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','115/75',90,65,58),(2,1,'2025-11-14',7.5,6,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','119/78',96,67,58.3),(3,1,'2025-11-15',8.5,7,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','123/81',102,69,58.6),(4,2,'2025-11-16',7.5,6,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','119/78',96,67,59),(5,2,'2025-11-17',8.5,7,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','123/81',102,69,59.3),(6,2,'2025-11-18',9.5,8,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','127/84',108,71,59.6),(7,3,'2025-11-19',8.5,7,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','123/81',102,69,60),(8,3,'2025-11-20',9.5,8,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','127/84',108,71,60.3),(9,3,'2025-11-21',6.5,9,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','131/75',90,73,60.6),(10,4,'2025-11-22',9.5,8,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','127/84',108,71,61),(11,4,'2025-11-23',6.5,9,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','131/75',90,73,61.3),(12,4,'2025-11-24',7.5,5,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','115/78',96,75,61.6),(13,5,'2025-11-25',6.5,9,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','131/75',90,73,62),(14,5,'2025-11-26',7.5,5,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','115/78',96,75,62.3),(15,5,'2025-11-27',8.5,6,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','119/81',102,65,62.6),(16,6,'2025-11-28',7.5,5,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','115/78',96,75,63),(17,6,'2025-11-29',8.5,6,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','119/81',102,65,63.3),(18,6,'2025-11-30',9.5,7,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','123/84',108,67,63.6),(19,7,'2025-12-01',8.5,6,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','119/81',102,65,64),(20,7,'2025-12-02',9.5,7,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','123/84',108,67,64.3),(21,7,'2025-12-03',6.5,8,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','127/75',90,69,64.6),(22,8,'2025-12-04',9.5,7,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','123/84',108,67,65),(23,8,'2025-12-05',6.5,8,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','127/75',90,69,65.3),(24,8,'2025-12-06',7.5,9,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','131/78',96,71,65.6),(25,9,'2025-12-07',6.5,8,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','127/75',90,69,66),(26,9,'2025-12-08',7.5,9,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','131/78',96,71,66.3),(27,9,'2025-12-09',8.5,5,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','115/81',102,73,66.6),(28,10,'2025-12-10',7.5,9,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','131/78',96,71,67),(29,10,'2025-12-11',8.5,5,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','115/81',102,73,67.3),(30,10,'2025-12-12',9.5,6,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','119/84',108,75,67.6),(31,11,'2025-12-13',8.5,5,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','115/81',102,73,68),(32,11,'2025-12-14',9.5,6,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','119/84',108,75,68.3),(33,11,'2025-12-15',6.5,7,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','123/75',90,65,68.6),(34,12,'2025-12-16',9.5,6,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','119/84',108,75,69),(35,12,'2025-12-17',6.5,7,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','123/75',90,65,69.3),(36,12,'2025-12-18',7.5,8,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','127/78',96,67,69.6),(37,13,'2025-12-19',6.5,7,'Caminata de 25 minutos','Menú balanceado día 1','Sin síntomas reportados','123/75',90,65,70),(38,13,'2025-12-20',7.5,8,'Yoga de 35 minutos','Menú balanceado día 2','Cansancio leve','127/78',96,67,70.3),(39,13,'2025-12-21',8.5,9,'Ciclismo de 45 minutos','Menú balanceado día 3','Sin síntomas reportados','131/81',102,69,70.6);
/*!40000 ALTER TABLE `daily_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permits`
--

DROP TABLE IF EXISTS `permits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permits`
--

LOCK TABLES `permits` WRITE;
/*!40000 ALTER TABLE `permits` DISABLE KEYS */;
INSERT INTO `permits` VALUES (1,'create_user'),(2,'edit_user'),(3,'delete_user'),(4,'view_health_records'),(5,'edit_health_records'),(6,'delete_health_records'),(7,'upload_files'),(8,'delete_files');
/*!40000 ALTER TABLE `permits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permits`
--

DROP TABLE IF EXISTS `role_permits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int DEFAULT NULL,
  `permit_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  KEY `permit_id` (`permit_id`),
  CONSTRAINT `role_permits_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `role_permits_ibfk_2` FOREIGN KEY (`permit_id`) REFERENCES `permits` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permits`
--

LOCK TABLES `role_permits` WRITE;
/*!40000 ALTER TABLE `role_permits` DISABLE KEYS */;
INSERT INTO `role_permits` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,1,5),(6,1,6),(7,1,7),(8,1,8),(9,2,4),(10,2,5),(11,2,7);
/*!40000 ALTER TABLE `role_permits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin'),(2,'user');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Lucía Torres',34,'lucia.admin@mail.com',1),(2,'Andrés Mejía',37,'andres.admin@mail.com',1),(3,'María Carvajal',32,'maria.admin@mail.com',1),(4,'Carlos Pérez',28,'carlos.user@mail.com',2),(5,'Laura Gómez',25,'laura.user@mail.com',2),(6,'Felipe Ríos',22,'felipe.user@mail.com',2),(7,'Daniela Hurtado',31,'daniela.user@mail.com',2),(8,'Elena Vivas',27,'elena.user@mail.com',2),(9,'Mateo Bernal',29,'mateo.user@mail.com',2),(10,'Sara Villada',24,'sara.user@mail.com',2),(11,'Nicolás Molina',33,'nicolas.user@mail.com',2),(12,'Juana Velasco',26,'juana.user@mail.com',2),(13,'David Valencia',30,'david.user@mail.com',2);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-04  4:24:52
