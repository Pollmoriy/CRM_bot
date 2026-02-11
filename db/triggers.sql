-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: business_manager
-- ------------------------------------------------------
-- Server version	9.4.0

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
-- Table structure for table `auditlogs`
--

DROP TABLE IF EXISTS `auditlogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditlogs` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `id_user` int DEFAULT NULL,
  `table_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action` enum('insert','update','delete') COLLATE utf8mb4_unicode_ci NOT NULL,
  `record_id` int DEFAULT NULL,
  `action_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `details` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_log`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `auditlogs_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=163 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditlogs`
--

LOCK TABLES `auditlogs` WRITE;
/*!40000 ALTER TABLE `auditlogs` DISABLE KEYS */;
INSERT INTO `auditlogs` VALUES (1,NULL,'clients','insert',1,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Сергей Смирнов\"'),(2,NULL,'clients','insert',2,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Екатерина Орлова\"'),(3,NULL,'clients','insert',3,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Дмитрий Павлов\"'),(4,NULL,'clients','insert',4,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Ольга Кравцова\"'),(5,NULL,'clients','insert',5,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Алексей Громов\"'),(6,NULL,'clients','insert',6,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Ирина Смирнова\"'),(7,NULL,'clients','insert',7,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Виктор Захаров\"'),(8,NULL,'clients','insert',8,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Татьяна Белова\"'),(9,NULL,'clients','insert',9,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Андрей Николаев\"'),(10,NULL,'clients','insert',10,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Светлана Федорова\"'),(11,NULL,'clients','insert',11,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Максим Егоров\"'),(12,NULL,'clients','insert',12,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Алина Васильева\"'),(13,NULL,'clients','insert',13,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Константин Попов\"'),(14,NULL,'clients','insert',14,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Юлия Козлова\"'),(15,NULL,'clients','insert',15,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Павел Сидоров\"'),(16,NULL,'clients','insert',16,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Елена Морозова\"'),(17,NULL,'clients','insert',17,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Сергей Волков\"'),(18,NULL,'clients','insert',18,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Наталья Кравцова\"'),(19,NULL,'clients','insert',19,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Олег Кузнецов\"'),(20,NULL,'clients','insert',20,'2025-12-16 18:16:09','Триггер: добавлен клиент \"Анна Иванова\"'),(21,NULL,'deals','insert',1,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка сайта для Смирнова\", \"id_client\": 1, \"id_manager\": 2}, \"type\": \"insert\"}'),(22,NULL,'deals','insert',2,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Маркетинговая кампания для Орловой\", \"id_client\": 2, \"id_manager\": 2}, \"type\": \"insert\"}'),(23,NULL,'deals','insert',3,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"CRM внедрение для Павлова\", \"id_client\": 3, \"id_manager\": 2}, \"type\": \"insert\"}'),(24,NULL,'deals','insert',4,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": 2}, \"type\": \"insert\"}'),(25,NULL,'deals','insert',5,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"SEO оптимизация для Громова\", \"id_client\": 5, \"id_manager\": 2}, \"type\": \"insert\"}'),(26,NULL,'deals','insert',6,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Рекламная кампания для Смирновой\", \"id_client\": 6, \"id_manager\": 2}, \"type\": \"insert\"}'),(27,NULL,'deals','insert',7,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Аудит для Захарова\", \"id_client\": 7, \"id_manager\": 2}, \"type\": \"insert\"}'),(28,NULL,'deals','insert',8,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка лендинга для Беловой\", \"id_client\": 8, \"id_manager\": 2}, \"type\": \"insert\"}'),(29,NULL,'deals','insert',9,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Долгосрочный контракт Николаева\", \"id_client\": 9, \"id_manager\": 2}, \"type\": \"insert\"}'),(30,NULL,'deals','insert',10,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"VIP проект Федоровой\", \"id_client\": 10, \"id_manager\": 2}, \"type\": \"insert\"}'),(31,NULL,'deals','insert',11,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"SEO аудит для Егорова\", \"id_client\": 11, \"id_manager\": 2}, \"type\": \"insert\"}'),(32,NULL,'deals','insert',12,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сайт для Васильевой\", \"id_client\": 12, \"id_manager\": 2}, \"type\": \"insert\"}'),(33,NULL,'deals','insert',13,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Разработка портала для Попова\", \"id_client\": 13, \"id_manager\": 2}, \"type\": \"insert\"}'),(34,NULL,'deals','insert',14,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP сопровождение Козловой\", \"id_client\": 14, \"id_manager\": 2}, \"type\": \"insert\"}'),(35,NULL,'deals','insert',15,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Новая\", \"deal_name\": \"Сайт для Сидорова\", \"id_client\": 15, \"id_manager\": 2}, \"type\": \"insert\"}'),(36,NULL,'deals','insert',16,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Реклама для Морозовой\", \"id_client\": 16, \"id_manager\": 2}, \"type\": \"insert\"}'),(37,NULL,'deals','insert',17,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"SEO для Волкова\", \"id_client\": 17, \"id_manager\": 2}, \"type\": \"insert\"}'),(38,NULL,'deals','insert',18,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"CRM настройка для Кравцовой\", \"id_client\": 18, \"id_manager\": 2}, \"type\": \"insert\"}'),(39,NULL,'deals','insert',19,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Оптимизация для Кузнецова\", \"id_client\": 19, \"id_manager\": 2}, \"type\": \"insert\"}'),(40,NULL,'deals','insert',20,'2025-12-16 18:19:10','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP проект Ивановой\", \"id_client\": 20, \"id_manager\": 2}, \"type\": \"insert\"}'),(41,NULL,'users','insert',1,'2025-01-10 06:00:00','Создан админ'),(42,NULL,'clients','insert',1,'2025-01-12 11:00:00','Добавлен клиент Смирнов'),(43,NULL,'deals','insert',1,'2025-01-15 06:00:00','Создана сделка для Смирнова'),(44,NULL,'tasks','insert',1,'2025-01-16 07:00:00','Создана задача прототип сайта'),(45,NULL,'notifications','insert',1,'2025-01-18 15:00:00','Уведомление о завершении задачи'),(46,NULL,'clients','insert',2,'2025-02-18 12:00:00','Добавлен клиент Орлова'),(47,NULL,'deals','insert',2,'2025-02-20 07:00:00','Создана сделка маркетинг'),(48,NULL,'tasks','insert',2,'2025-02-21 08:00:00','Задача рекламные материалы'),(49,NULL,'notifications','insert',2,'2025-02-28 06:00:00','Напоминание по дедлайну'),(50,NULL,'clients','insert',3,'2025-03-01 06:30:00','Добавлен клиент Павлов'),(51,NULL,'deals','insert',3,'2025-03-05 06:00:00','Создана сделка CRM'),(52,NULL,'tasks','insert',3,'2025-03-06 07:00:00','Задача настройка CRM'),(53,NULL,'notifications','insert',3,'2025-03-05 07:00:00','Уведомление о новой задаче'),(54,NULL,'clients','insert',15,'2025-12-01 06:00:00','Добавлен клиент Сидоров'),(55,NULL,'deals','insert',15,'2025-12-01 06:00:00','Создана сделка сайт'),(56,NULL,'tasks','insert',15,'2025-12-02 06:00:00','Задача сайт для Сидорова'),(57,NULL,'notifications','insert',15,'2025-12-02 06:00:00','Уведомление о новой задаче'),(58,NULL,'deals','update',20,'2025-12-10 11:00:00','VIP проект Ивановой завершен'),(59,NULL,'notifications','insert',20,'2025-12-10 11:00:00','Уведомление о завершении VIP проекта'),(60,NULL,'deals','update',1,'2025-12-16 22:08:30','Смена стадии: Закрыта → Закрыта'),(61,NULL,'deals','update',1,'2025-12-16 22:08:30','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка сайта для Смирнова\", \"id_client\": 1, \"id_manager\": 3}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка сайта для Смирнова\", \"id_client\": 1, \"id_manager\": 2}, \"type\": \"update\"}'),(62,NULL,'deals','update',2,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(63,NULL,'deals','update',2,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Маркетинговая кампания для Орловой\", \"id_client\": 2, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Маркетинговая кампания для Орловой\", \"id_client\": 2, \"id_manager\": 2}, \"type\": \"update\"}'),(64,NULL,'deals','update',3,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(65,NULL,'deals','update',3,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"CRM внедрение для Павлова\", \"id_client\": 3, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"CRM внедрение для Павлова\", \"id_client\": 3, \"id_manager\": 2}, \"type\": \"update\"}'),(66,NULL,'deals','update',4,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(67,NULL,'deals','update',4,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": 3}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": 2}, \"type\": \"update\"}'),(68,NULL,'deals','update',5,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(69,NULL,'deals','update',5,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"SEO оптимизация для Громова\", \"id_client\": 5, \"id_manager\": 7}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"SEO оптимизация для Громова\", \"id_client\": 5, \"id_manager\": 2}, \"type\": \"update\"}'),(70,NULL,'deals','update',6,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(71,NULL,'deals','update',6,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Рекламная кампания для Смирновой\", \"id_client\": 6, \"id_manager\": 7}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Рекламная кампания для Смирновой\", \"id_client\": 6, \"id_manager\": 2}, \"type\": \"update\"}'),(72,NULL,'deals','update',7,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(73,NULL,'deals','update',7,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Аудит для Захарова\", \"id_client\": 7, \"id_manager\": 7}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Аудит для Захарова\", \"id_client\": 7, \"id_manager\": 2}, \"type\": \"update\"}'),(74,NULL,'deals','update',8,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(75,NULL,'deals','update',8,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка лендинга для Беловой\", \"id_client\": 8, \"id_manager\": 7}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка лендинга для Беловой\", \"id_client\": 8, \"id_manager\": 2}, \"type\": \"update\"}'),(76,NULL,'deals','update',9,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(77,NULL,'deals','update',9,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Долгосрочный контракт Николаева\", \"id_client\": 9, \"id_manager\": 7}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Долгосрочный контракт Николаева\", \"id_client\": 9, \"id_manager\": 2}, \"type\": \"update\"}'),(78,NULL,'deals','update',10,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(79,NULL,'deals','update',10,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"VIP проект Федоровой\", \"id_client\": 10, \"id_manager\": 7}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"VIP проект Федоровой\", \"id_client\": 10, \"id_manager\": 2}, \"type\": \"update\"}'),(80,NULL,'deals','update',11,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(81,NULL,'deals','update',11,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"SEO аудит для Егорова\", \"id_client\": 11, \"id_manager\": 10}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"SEO аудит для Егорова\", \"id_client\": 11, \"id_manager\": 2}, \"type\": \"update\"}'),(82,NULL,'deals','update',12,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(83,NULL,'deals','update',12,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сайт для Васильевой\", \"id_client\": 12, \"id_manager\": 10}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Сайт для Васильевой\", \"id_client\": 12, \"id_manager\": 2}, \"type\": \"update\"}'),(84,NULL,'deals','update',13,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(85,NULL,'deals','update',13,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Разработка портала для Попова\", \"id_client\": 13, \"id_manager\": 10}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Разработка портала для Попова\", \"id_client\": 13, \"id_manager\": 2}, \"type\": \"update\"}'),(86,NULL,'deals','update',14,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(87,NULL,'deals','update',14,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP сопровождение Козловой\", \"id_client\": 14, \"id_manager\": 1}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP сопровождение Козловой\", \"id_client\": 14, \"id_manager\": 2}, \"type\": \"update\"}'),(88,NULL,'deals','update',15,'2025-12-16 22:08:31','Смена стадии: Новая → Новая'),(89,NULL,'deals','update',15,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Новая\", \"deal_name\": \"Сайт для Сидорова\", \"id_client\": 15, \"id_manager\": 1}, \"old\": {\"stage\": \"Новая\", \"deal_name\": \"Сайт для Сидорова\", \"id_client\": 15, \"id_manager\": 2}, \"type\": \"update\"}'),(90,NULL,'deals','update',16,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(91,NULL,'deals','update',16,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Реклама для Морозовой\", \"id_client\": 16, \"id_manager\": 1}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Реклама для Морозовой\", \"id_client\": 16, \"id_manager\": 2}, \"type\": \"update\"}'),(92,NULL,'deals','update',17,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(93,NULL,'deals','update',17,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"SEO для Волкова\", \"id_client\": 17, \"id_manager\": 1}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"SEO для Волкова\", \"id_client\": 17, \"id_manager\": 2}, \"type\": \"update\"}'),(94,NULL,'deals','update',18,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(95,NULL,'deals','update',18,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"CRM настройка для Кравцовой\", \"id_client\": 18, \"id_manager\": 1}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"CRM настройка для Кравцовой\", \"id_client\": 18, \"id_manager\": 2}, \"type\": \"update\"}'),(96,NULL,'deals','update',19,'2025-12-16 22:08:31','Смена стадии: В работе → В работе'),(97,NULL,'deals','update',19,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Оптимизация для Кузнецова\", \"id_client\": 19, \"id_manager\": 1}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Оптимизация для Кузнецова\", \"id_client\": 19, \"id_manager\": 2}, \"type\": \"update\"}'),(98,NULL,'deals','update',20,'2025-12-16 22:08:31','Смена стадии: Закрыта → Закрыта'),(99,NULL,'deals','update',20,'2025-12-16 22:08:31','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP проект Ивановой\", \"id_client\": 20, \"id_manager\": 14}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"VIP проект Ивановой\", \"id_client\": 20, \"id_manager\": 2}, \"type\": \"update\"}'),(100,NULL,'deals','update',1,'2025-12-18 13:28:30','Смена стадии: Закрыта → Закрыта'),(101,NULL,'deals','update',1,'2025-12-18 13:28:30','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка сайта для Смирнова\", \"id_client\": 1, \"id_manager\": 3}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Разработка сайта для Смирнова\", \"id_client\": 1, \"id_manager\": 3}, \"type\": \"update\"}'),(102,NULL,'tasks','update',1,'2025-12-18 13:28:30','Статус задачи \"Создать прототип сайта\" изменён: done → done'),(103,NULL,'deals','update',2,'2025-12-18 13:28:30','Смена стадии: В работе → В работе'),(104,NULL,'deals','update',2,'2025-12-18 13:28:30','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Маркетинговая кампания для Орловой\", \"id_client\": 2, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Маркетинговая кампания для Орловой\", \"id_client\": 2, \"id_manager\": 3}, \"type\": \"update\"}'),(105,NULL,'tasks','update',2,'2025-12-18 13:28:30','Статус задачи \"Подготовить рекламные материалы\" изменён: in_progress → in_progress'),(106,NULL,'deals','update',3,'2025-12-18 13:28:30','Смена стадии: В работе → В работе'),(107,NULL,'deals','update',3,'2025-12-18 13:28:30','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"CRM внедрение для Павлова\", \"id_client\": 3, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"CRM внедрение для Павлова\", \"id_client\": 3, \"id_manager\": 3}, \"type\": \"update\"}'),(108,NULL,'tasks','update',3,'2025-12-18 13:28:30','Статус задачи \"Настроить CRM\" изменён: in_progress → in_progress'),(109,NULL,'deals','update',4,'2025-12-18 13:28:30','Смена стадии: Закрыта → Закрыта'),(110,NULL,'deals','update',4,'2025-12-18 13:28:30','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": 3}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": 3}, \"type\": \"update\"}'),(111,NULL,'tasks','update',4,'2025-12-18 13:28:30','Статус задачи \"Провести консультацию\" изменён: done → done'),(112,NULL,'clients','insert',21,'2025-12-19 09:57:39','Триггер: добавлен клиент \"? Клиенты\"'),(113,NULL,'clients','insert',21,'2025-12-19 09:57:39','Добавлен клиент: ? Клиенты'),(120,NULL,'deals','update',10,'2025-12-27 08:37:01','Смена стадии: В работе → В работе'),(121,NULL,'deals','update',10,'2025-12-27 08:37:01','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"VIP проект Федоровой\", \"id_client\": null, \"id_manager\": null}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"VIP проект Федоровой\", \"id_client\": 10, \"id_manager\": null}, \"type\": \"update\"}'),(122,NULL,'deals','insert',21,'2025-12-27 08:38:40','{\"new\": {\"stage\": \"Новая\", \"deal_name\": \"Купить хлеб надо\", \"id_client\": 4, \"id_manager\": 24}, \"type\": \"insert\"}'),(123,NULL,'deals','update',4,'2025-12-27 08:40:18','Смена стадии: Закрыта → Закрыта'),(124,NULL,'deals','update',4,'2025-12-27 08:40:18','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сео Кравцова\", \"id_client\": 4, \"id_manager\": null}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Консультация для Кравцовой\", \"id_client\": 4, \"id_manager\": null}, \"type\": \"update\"}'),(125,NULL,'deals','update',4,'2025-12-27 08:40:54','Смена стадии: Закрыта → Закрыта'),(126,NULL,'deals','update',4,'2025-12-27 08:40:54','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"CEO Кравцева\", \"id_client\": 4, \"id_manager\": null}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сео Кравцова\", \"id_client\": 4, \"id_manager\": null}, \"type\": \"update\"}'),(127,NULL,'deals','delete',4,'2025-12-27 08:41:09','{\"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"CEO Кравцева\", \"id_client\": 4, \"id_manager\": null}, \"type\": \"delete\"}'),(128,NULL,'clients','insert',1,'2025-12-27 08:57:29','Триггер: добавлен клиент \"ООО Ромашка\"'),(129,NULL,'clients','insert',2,'2025-12-27 08:57:29','Триггер: добавлен клиент \"ИП Васильев\"'),(130,NULL,'clients','insert',3,'2025-12-27 08:57:29','Триггер: добавлен клиент \"ЗАО Альфа\"'),(131,NULL,'clients','insert',4,'2025-12-27 08:57:29','Триггер: добавлен клиент \"ООО Бета\"'),(132,NULL,'clients','insert',5,'2025-12-27 08:57:29','Триггер: добавлен клиент \"ИП Кузнецов\"'),(133,NULL,'deals','insert',1,'2025-12-27 08:57:29','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 1\", \"id_client\": 1, \"id_manager\": 2}, \"type\": \"insert\"}'),(134,NULL,'deals','insert',2,'2025-12-27 08:57:29','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 2}, \"type\": \"insert\"}'),(135,NULL,'deals','insert',3,'2025-12-27 08:57:29','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"type\": \"insert\"}'),(136,NULL,'deals','insert',4,'2025-12-27 08:57:29','{\"new\": {\"stage\": \"Новая\", \"deal_name\": \"Сделка 4\", \"id_client\": 4, \"id_manager\": 3}, \"type\": \"insert\"}'),(137,NULL,'deals','insert',5,'2025-12-27 08:57:29','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 5\", \"id_client\": 5, \"id_manager\": 2}, \"type\": \"insert\"}'),(138,3,'deals','update',3,'2025-12-27 08:59:37','Смена стадии: В работе → В работе'),(139,NULL,'deals','update',3,'2025-12-27 08:59:37','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"type\": \"update\"}'),(140,8,'tasks','update',7,'2025-12-27 08:59:37','Статус задачи \"Проверка документов\" изменён: done → done'),(141,8,'Tasks','update',7,'2025-12-27 09:00:10','Статус задачи изменён с \"done\" на \"in_progress\"'),(142,3,'deals','update',3,'2025-12-27 09:00:10','Смена стадии: В работе → В работе'),(143,NULL,'deals','update',3,'2025-12-27 09:00:10','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"type\": \"update\"}'),(144,8,'tasks','update',7,'2025-12-27 09:00:10','Статус задачи \"Проверка документов\" изменён: done → in_progress'),(145,8,'Tasks','update',7,'2025-12-27 09:00:20','Статус задачи изменён с \"in_progress\" на \"done\"'),(146,3,'deals','update',3,'2025-12-27 09:00:20','Смена стадии: В работе → В работе'),(147,NULL,'deals','update',3,'2025-12-27 09:00:20','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 3\", \"id_client\": 3, \"id_manager\": 3}, \"type\": \"update\"}'),(148,8,'tasks','update',7,'2025-12-27 09:00:20','Статус задачи \"Проверка документов\" изменён: in_progress → done'),(149,8,'deals','update',4,'2025-12-27 09:02:49','Смена стадии: Новая → Новая'),(150,NULL,'deals','update',4,'2025-12-27 09:02:49','{\"new\": {\"stage\": \"Новая\", \"deal_name\": \"Сделка 4\", \"id_client\": 4, \"id_manager\": 8}, \"old\": {\"stage\": \"Новая\", \"deal_name\": \"Сделка 4\", \"id_client\": 4, \"id_manager\": 3}, \"type\": \"update\"}'),(151,8,'deals','update',5,'2025-12-27 09:02:49','Смена стадии: В работе → В работе'),(152,NULL,'deals','update',5,'2025-12-27 09:02:49','{\"new\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 5\", \"id_client\": 5, \"id_manager\": 8}, \"old\": {\"stage\": \"В работе\", \"deal_name\": \"Сделка 5\", \"id_client\": 5, \"id_manager\": 2}, \"type\": \"update\"}'),(153,8,'deals','update',2,'2025-12-27 09:02:49','Смена стадии: Закрыта → Закрыта'),(154,NULL,'deals','update',2,'2025-12-27 09:02:49','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 8}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 2}, \"type\": \"update\"}'),(155,10,'Tasks','update',9,'2025-12-27 11:35:55','Статус задачи изменён с \"new\" на \"done\"'),(156,8,'deals','update',2,'2025-12-27 11:35:55','Смена стадии: Закрыта → Закрыта'),(157,NULL,'deals','update',2,'2025-12-27 11:35:55','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 8}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 8}, \"type\": \"update\"}'),(158,10,'tasks','update',9,'2025-12-27 11:35:55','Статус задачи \"Купи попить\" изменён: new → done'),(159,8,'deals','update',2,'2025-12-27 11:36:23','Смена стадии: Закрыта → Закрыта'),(160,NULL,'deals','update',2,'2025-12-27 11:36:23','{\"new\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 8}, \"old\": {\"stage\": \"Закрыта\", \"deal_name\": \"Сделка 2\", \"id_client\": 2, \"id_manager\": 8}, \"type\": \"update\"}'),(161,10,'tasks','update',9,'2025-12-27 11:36:23','Статус задачи \"Купи попить\" изменён: done → done'),(162,NULL,'clients','insert',6,'2025-12-27 11:38:06','Триггер: добавлен клиент \"Сабрина\"');
/*!40000 ALTER TABLE `auditlogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id_client` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telegram` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `added_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `segment` enum('new','regular','vip') COLLATE utf8mb4_unicode_ci DEFAULT 'new',
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_client`),
  KEY `idx_clients_full_name` (`full_name`),
  KEY `idx_clients_added_date` (`added_date`),
  KEY `idx_clients_segment` (`segment`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
INSERT INTO `clients` VALUES (1,'ООО Ромашка','+375297654321','romashka_bot','1995-06-15','2025-12-27 08:57:29','new','Новый клиент, заинтересован в услугах.'),(2,'ИП Васильев','+375296543210','vasilev_ip','1988-11-23','2025-12-27 08:57:29','regular','Работает с нами с 2022 года.'),(3,'ЗАО Альфа','+375295432109','alpha_zao','1980-01-05','2025-12-27 08:57:29','vip','VIP-клиент, крупные сделки.'),(4,'ООО Бета','+375294321098','beta_bot','1990-03-12','2025-12-27 08:57:29','regular','Средние объемы заказов.'),(5,'ИП Кузнецов','+375293210987','kuznetsov_ip','1993-07-30','2025-12-27 08:57:29','new','Новый клиент, интересуются аналитикой.'),(6,'Сабрина','+375296144070','luckimi','2007-12-27','2025-12-27 08:57:29','vip',NULL);
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_insert_client` AFTER INSERT ON `clients` FOR EACH ROW BEGIN
    INSERT INTO auditlogs (id_user, table_name, action, record_id, details)
    VALUES (NULL, 'clients', 'insert', NEW.id_client,
            CONCAT('Триггер: добавлен клиент "', NEW.full_name, '"'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `deals`
--

DROP TABLE IF EXISTS `deals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deals` (
  `id_deal` int NOT NULL AUTO_INCREMENT,
  `deal_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_client` int DEFAULT NULL,
  `id_manager` int DEFAULT NULL,
  `progress` tinyint DEFAULT '0',
  `is_completed` tinyint(1) DEFAULT '0',
  `date_created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_completed` date DEFAULT NULL,
  `stage` enum('Новая','В работе','Закрыта','Приостановлена') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Новая',
  PRIMARY KEY (`id_deal`),
  KEY `id_client` (`id_client`),
  KEY `id_manager` (`id_manager`),
  CONSTRAINT `deals_ibfk_1` FOREIGN KEY (`id_client`) REFERENCES `clients` (`id_client`) ON DELETE SET NULL,
  CONSTRAINT `deals_ibfk_2` FOREIGN KEY (`id_manager`) REFERENCES `users` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deals`
--

LOCK TABLES `deals` WRITE;
/*!40000 ALTER TABLE `deals` DISABLE KEYS */;
INSERT INTO `deals` VALUES (1,'Сделка 1',1,2,50,0,'2025-12-27 08:57:29',NULL,'В работе'),(2,'Сделка 2',2,8,100,1,'2025-12-27 08:57:29','2025-12-27','Закрыта'),(3,'Сделка 3',3,3,50,0,'2025-12-27 08:57:29',NULL,'В работе'),(4,'Сделка 4',4,8,0,0,'2025-12-27 08:57:29',NULL,'Новая'),(5,'Сделка 5',5,8,75,0,'2025-12-27 08:57:29',NULL,'В работе');
/*!40000 ALTER TABLE `deals` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_deals_after_insert` AFTER INSERT ON `deals` FOR EACH ROW BEGIN
  INSERT INTO auditlogs (id_user, table_name, action, record_id, action_time, details)
  VALUES (
    COALESCE(@current_user_id, NULL),
    'deals',
    'insert',
    NEW.id_deal,
    NOW(),
    JSON_OBJECT(
      'type', 'insert',
      'new', JSON_OBJECT(
         'deal_name', NEW.deal_name,
         'id_client', NEW.id_client,
         'id_manager', NEW.id_manager,
         'stage', NEW.stage
      )
    )
  );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `deals_after_update` AFTER UPDATE ON `deals` FOR EACH ROW BEGIN
  INSERT INTO auditlogs (id_user, table_name, action, record_id, details)
  VALUES (NEW.id_manager, 'deals', 'update', NEW.id_deal,
          CONCAT('Смена стадии: ', OLD.stage, ' → ', NEW.stage));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_deals_after_update` AFTER UPDATE ON `deals` FOR EACH ROW BEGIN
  INSERT INTO auditlogs (id_user, table_name, action, record_id, action_time, details)
  VALUES (
    COALESCE(@current_user_id, NULL),
    'deals',
    'update',
    NEW.id_deal,
    NOW(),
    JSON_OBJECT(
      'type', 'update',
      'old', JSON_OBJECT(
         'deal_name', OLD.deal_name,
         'id_client', OLD.id_client,
         'id_manager', OLD.id_manager,
         'stage', OLD.stage
      ),
      'new', JSON_OBJECT(
         'deal_name', NEW.deal_name,
         'id_client', NEW.id_client,
         'id_manager', NEW.id_manager,
         'stage', NEW.stage
      )
    )
  );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_manual_deal_close` AFTER UPDATE ON `deals` FOR EACH ROW BEGIN
    -- Проверяем, что стадия изменилась на Закрыта вручную
    IF OLD.stage <> NEW.stage AND NEW.stage = 'Закрыта' THEN
        INSERT INTO AuditLogs (id_user, table_name, action, record_id, details, action_time)
        VALUES (
            NULL, -- если не знаем конкретного пользователя, можно NULL или id менеджера
            'Deals',
            'update',
            NEW.id_deal,
            CONCAT('Сделка закрыта вручную (статус изменён с "', OLD.stage, '" на "', NEW.stage, '")'),
            NOW()
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_deals_after_delete` AFTER DELETE ON `deals` FOR EACH ROW BEGIN
  INSERT INTO auditlogs (id_user, table_name, action, record_id, action_time, details)
  VALUES (
    COALESCE(@current_user_id, NULL),
    'deals',
    'delete',
    OLD.id_deal,
    NOW(),
    JSON_OBJECT(
      'type', 'delete',
      'old', JSON_OBJECT(
        'deal_name', OLD.deal_name,
        'id_client', OLD.id_client,
        'id_manager', OLD.id_manager,
        'stage', OLD.stage
      )
    )
  );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `interactions`
--

DROP TABLE IF EXISTS `interactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interactions` (
  `id_interaction` int NOT NULL AUTO_INCREMENT,
  `id_client` int DEFAULT NULL,
  `id_user` int DEFAULT NULL,
  `interaction_type` enum('call','meeting','message','email') COLLATE utf8mb4_unicode_ci DEFAULT 'message',
  `description` text COLLATE utf8mb4_unicode_ci,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_interaction`),
  KEY `id_client` (`id_client`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `interactions_ibfk_1` FOREIGN KEY (`id_client`) REFERENCES `clients` (`id_client`) ON DELETE CASCADE,
  CONSTRAINT `interactions_ibfk_2` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interactions`
--

LOCK TABLES `interactions` WRITE;
/*!40000 ALTER TABLE `interactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `interactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mailings`
--

DROP TABLE IF EXISTS `mailings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mailings` (
  `id_mailing` int NOT NULL AUTO_INCREMENT,
  `mailing_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `target_segment` enum('new','regular','vip','all') COLLATE utf8mb4_unicode_ci DEFAULT 'all',
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mailing`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `mailings_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mailings`
--

LOCK TABLES `mailings` WRITE;
/*!40000 ALTER TABLE `mailings` DISABLE KEYS */;
INSERT INTO `mailings` VALUES (1,'manual','Рассылка тестовая','new',NULL,'2025-12-18 10:21:09'),(2,'manual_2025-12-27','Привет {name} как дела?','all',22,'2025-12-27 08:46:43'),(3,'manual_2025-12-27','? Рассылки','vip',8,'2025-12-27 11:39:10');
/*!40000 ALTER TABLE `mailings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id_notification` int NOT NULL AUTO_INCREMENT,
  `id_employee` int DEFAULT NULL,
  `id_task` int DEFAULT NULL,
  `id_deal` int DEFAULT NULL,
  `title` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_notification`),
  KEY `id_employee` (`id_employee`),
  KEY `id_task` (`id_task`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`id_employee`) REFERENCES `users` (`id_user`) ON DELETE CASCADE,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`id_task`) REFERENCES `tasks` (`id_task`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (26,30,21,NULL,'Новая задача: Сделать верстку','Вам назначена новая задача по сделке ID 1.\nОписание: Надо срочно очень',0,'2025-12-27 08:43:34'),(27,30,21,1,'Новая задача','? Новая задача <b>Сделать верстку</b> для сделки <b>Разработка сайта для Смирнова</b>.',0,'2025-12-27 08:43:34'),(28,4,1,NULL,'Новая задача: Позвонить клиенту','Вам назначена новая задача по сделке ID 1.\nОписание: Связаться с клиентом по сделке 1',0,'2025-12-27 08:57:29'),(29,5,2,NULL,'Новая задача: Отправить предложение','Вам назначена новая задача по сделке ID 1.\nОписание: Подготовить коммерческое предложение для сделки 1',0,'2025-12-27 08:57:29'),(30,4,3,NULL,'Новая задача: Согласовать условия','Вам назначена новая задача по сделке ID 2.\nОписание: Обсудить условия сделки 2 с клиентом',0,'2025-12-27 08:57:29'),(31,6,4,NULL,'Новая задача: Подготовить отчет','Вам назначена новая задача по сделке ID 3.\nОписание: Сформировать отчет по сделке 3',0,'2025-12-27 08:57:29'),(32,7,5,NULL,'Новая задача: Запланировать встречу','Вам назначена новая задача по сделке ID 4.\nОписание: Назначить встречу с клиентом по сделке 4',0,'2025-12-27 08:57:29'),(33,5,6,NULL,'Новая задача: Отправка документации','Вам назначена новая задача по сделке ID 5.\nОписание: Отправить договор клиенту по сделке 5',0,'2025-12-27 08:57:29'),(34,6,7,NULL,'Новая задача: Проверка документов','Вам назначена новая задача по сделке ID 3.\nОписание: Проверить договор для ЗАО Альфа',0,'2025-12-27 08:57:29'),(35,4,8,NULL,'Новая задача: Напоминание клиенту','Вам назначена новая задача по сделке ID 2.\nОписание: Напомнить о встрече с ИП Васильев',0,'2025-12-27 08:57:29'),(36,10,9,NULL,'Новая задача: Купи попить','Вам назначена новая задача по сделке ID 2.\nОписание: -',0,'2025-12-27 11:33:27'),(37,10,9,2,'Новая задача','? Новая задача <b>Купи попить</b> для сделки <b>Сделка 2</b>.',0,'2025-12-27 11:33:27'),(38,8,NULL,2,'Сделка закрыта','✅ Сделка <b>Сделка 2</b> успешно закрыта.',0,'2025-12-27 11:34:41'),(39,4,1,1,'Напоминание о задаче','Задача <b>Позвонить клиенту</b> должна быть выполнена до <b>28.12.2025</b>.',0,'2025-12-27 11:34:41'),(40,6,4,3,'Напоминание о задаче','Задача <b>Подготовить отчет</b> должна быть выполнена до <b>30.12.2025</b>.',0,'2025-12-27 11:34:42'),(41,5,6,5,'Напоминание о задаче','Задача <b>Отправка документации</b> должна быть выполнена до <b>28.12.2025</b>.',0,'2025-12-27 11:34:42');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reports`
--

DROP TABLE IF EXISTS `reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reports` (
  `id_report` int NOT NULL AUTO_INCREMENT,
  `report_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `report_type` enum('summary','performance','sales','ai_analysis') COLLATE utf8mb4_unicode_ci DEFAULT 'summary',
  `generated_by` int DEFAULT NULL,
  `generated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ai_summary` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_report`),
  KEY `generated_by` (`generated_by`),
  CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`generated_by`) REFERENCES `users` (`id_user`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reports`
--

LOCK TABLES `reports` WRITE;
/*!40000 ALTER TABLE `reports` DISABLE KEYS */;
INSERT INTO `reports` VALUES (1,'Отчет по менеджеру Петрова','performance',2,'2025-12-27 08:57:29','Сотрудники выполняют задачи своевременно, есть небольшие задержки по сделке 1.'),(2,'Анализ сделок за декабрь','sales',1,'2025-12-27 08:57:29','Сделки закрыты в среднем на 65%, рекомендовано ускорить работу с новыми клиентами.'),(3,'Прогресс сделок и сотрудников','ai_analysis',1,'2025-12-27 08:57:29','Все задачи распределены, просроченных задач нет, сделка 2 полностью закрыта.'),(4,'Продажи по клиентам','summary',1,'2025-12-27 08:57:29','Топ-3 клиента: ЗАО Альфа, ИП Васильев, ООО Ромашка. Продажи растут в декабре.'),(5,'Воронка продаж','summary',1,'2025-12-27 08:57:29','Этапы сделки распределены: Новая - 1, В работе - 3, Закрыта - 1.'),(6,'Прогресс по периодам','performance',2,'2025-12-27 08:57:29','Динамика задач, сделок и продаж по неделям декабря показана на линейной диаграмме.'),(7,'Отчёт администратора за 365 дней','ai_analysis',8,'2025-12-27 09:17:54','Рекомендуется контролировать новые и приостановленные сделки, оптимизировать распределение задач и завершать приоритетные сделки.'),(8,'Отчёт администратора за 365 дней','ai_analysis',8,'2025-12-27 10:04:56','Рекомендуется контролировать новые и приостановленные сделки, оптимизировать распределение задач и завершать приоритетные сделки.');
/*!40000 ALTER TABLE `reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `id_task` int NOT NULL AUTO_INCREMENT,
  `task_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `id_employee` int DEFAULT NULL,
  `id_deal` int DEFAULT NULL,
  `status` enum('new','in_progress','done','overdue') COLLATE utf8mb4_unicode_ci DEFAULT 'new',
  `priority` enum('low','medium','high') COLLATE utf8mb4_unicode_ci DEFAULT 'medium',
  `deadline` date DEFAULT NULL,
  `date_completed` date DEFAULT NULL,
  PRIMARY KEY (`id_task`),
  KEY `id_employee` (`id_employee`),
  KEY `id_deal` (`id_deal`),
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`id_employee`) REFERENCES `users` (`id_user`) ON DELETE SET NULL,
  CONSTRAINT `tasks_ibfk_2` FOREIGN KEY (`id_deal`) REFERENCES `deals` (`id_deal`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
INSERT INTO `tasks` VALUES (1,'Позвонить клиенту','Связаться с клиентом по сделке 1',4,1,'in_progress','high','2025-12-28',NULL),(2,'Отправить предложение','Подготовить коммерческое предложение для сделки 1',5,1,'new','medium','2025-12-29',NULL),(3,'Согласовать условия','Обсудить условия сделки 2 с клиентом',4,2,'done','high','2025-12-15','2025-12-20'),(4,'Подготовить отчет','Сформировать отчет по сделке 3',6,3,'in_progress','medium','2025-12-30',NULL),(5,'Запланировать встречу','Назначить встречу с клиентом по сделке 4',7,4,'new','low','2026-01-05',NULL),(6,'Отправка документации','Отправить договор клиенту по сделке 5',5,5,'in_progress','high','2025-12-28',NULL),(7,'Проверка документов','Проверить договор для ЗАО Альфа',8,3,'done','medium','2025-12-25','2025-12-26'),(8,'Напоминание клиенту','Напомнить о встрече с ИП Васильев',4,2,'done','low','2025-12-19','2025-12-19'),(9,'Купи попить','-',10,2,'done','medium','2025-12-27',NULL);
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_task_insert` AFTER INSERT ON `tasks` FOR EACH ROW BEGIN
    INSERT INTO Notifications (id_employee, id_task, title, content)
    VALUES (
        NEW.id_employee,
        NEW.id_task,
        CONCAT('Новая задача: ', NEW.task_name),
        CONCAT('Вам назначена новая задача по сделке ID ', NEW.id_deal, '.\nОписание: ', NEW.description)
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_task_update` AFTER UPDATE ON `tasks` FOR EACH ROW BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO AuditLogs (id_user, table_name, action, record_id, details)
        VALUES (
            NEW.id_employee,
            'Tasks',
            'update',
            NEW.id_task,
            CONCAT('Статус задачи изменён с "', OLD.status, '" на "', NEW.status, '"')
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_task_status_change` AFTER UPDATE ON `tasks` FOR EACH ROW BEGIN
    DECLARE total_tasks INT;
    DECLARE completed_tasks INT;

    -- Считаем общее количество задач по сделке
    SELECT COUNT(*) INTO total_tasks
    FROM Tasks
    WHERE id_deal = NEW.id_deal;

    -- Считаем количество выполненных задач
    SELECT COUNT(*) INTO completed_tasks
    FROM Tasks
    WHERE id_deal = NEW.id_deal AND status = 'done';

    -- Если все задачи выполнены — обновляем сделку
    IF total_tasks > 0 AND total_tasks = completed_tasks THEN
        UPDATE Deals
        SET is_completed = TRUE,
            progress = 100,
            date_completed = CURRENT_DATE()
        WHERE id_deal = NEW.id_deal;
    ELSE
        UPDATE Deals
        SET is_completed = FALSE,
            progress = ROUND((completed_tasks / total_tasks) * 100)
        WHERE id_deal = NEW.id_deal;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_task_deadline_update` AFTER UPDATE ON `tasks` FOR EACH ROW BEGIN
    IF OLD.deadline <> NEW.deadline THEN
        INSERT INTO Notifications (id_employee, id_task, title, content)
        VALUES (
            NEW.id_employee,
            NEW.id_task,
            'Обновлён дедлайн задачи',
            CONCAT('Для задачи "', NEW.task_name, '" установлен новый срок: ', DATE_FORMAT(NEW.deadline, '%d.%m.%Y'))
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tasks_after_update` AFTER UPDATE ON `tasks` FOR EACH ROW BEGIN
  INSERT INTO auditlogs (id_user, table_name, action, record_id, details)
  VALUES (NEW.id_employee, 'tasks', 'update', NEW.id_task,
          CONCAT('Статус задачи "', OLD.task_name, '" изменён: ', OLD.status, ' → ', NEW.status));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_deal_stage_after_task_change` AFTER UPDATE ON `tasks` FOR EACH ROW BEGIN
    DECLARE total_tasks INT;
    DECLARE done_tasks INT;
    DECLARE in_progress_tasks INT;
    DECLARE overdue_tasks INT;
    DECLARE new_stage ENUM('Новая','В работе','Закрыта','Приостановлена');

    -- Считаем задачи по сделке
    SELECT COUNT(*) INTO total_tasks
    FROM tasks
    WHERE id_deal = NEW.id_deal;

    SELECT COUNT(*) INTO done_tasks
    FROM tasks
    WHERE id_deal = NEW.id_deal AND status = 'done';

    SELECT COUNT(*) INTO in_progress_tasks
    FROM tasks
    WHERE id_deal = NEW.id_deal AND status = 'in_progress';

    SELECT COUNT(*) INTO overdue_tasks
    FROM tasks
    WHERE id_deal = NEW.id_deal AND status = 'overdue';

    -- Логика изменения стадии сделки
    IF total_tasks = 0 THEN
        SET new_stage = 'Новая';
    ELSEIF done_tasks = total_tasks THEN
        SET new_stage = 'Закрыта';
    ELSEIF overdue_tasks > 0 THEN
        SET new_stage = 'Приостановлена';
    ELSE
        SET new_stage = 'В работе';
    END IF;

    -- Обновляем сделку, если стадия изменилась
    IF (SELECT stage FROM deals WHERE id_deal = NEW.id_deal) <> new_stage THEN
        UPDATE deals
        SET stage = new_stage
        WHERE id_deal = NEW.id_deal;

        -- Запись в лог
        INSERT INTO AuditLogs (id_user, table_name, action, record_id, details, action_time)
        VALUES (
            NEW.id_employee,
            'Deals',
            'update',
            NEW.id_deal,
            CONCAT('Стадия сделки автоматически изменена на "', new_stage, '"'),
            NOW()
        );
    END IF;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telegram_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('admin','manager','employee') COLLATE utf8mb4_unicode_ci DEFAULT 'employee',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `manager_id` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_user`),
  KEY `fk_manager` (`manager_id`),
  CONSTRAINT `fk_manager` FOREIGN KEY (`manager_id`) REFERENCES `users` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Иванов Сергей','+375291234567','ivanov_s','admin','2025-12-27 08:57:29',NULL,1),(2,'Петрова Анна','+375292345678','petrova_a','manager','2025-12-27 08:57:29',8,1),(3,'Сидоров Алексей','+375293456789','sidorov_a','manager','2025-12-27 08:57:29',1,1),(4,'Козлова Мария','+375291112233','kozlova_m','employee','2025-12-27 08:57:29',8,1),(5,'Морозов Дмитрий','+375292223344','morozov_d','employee','2025-12-27 08:57:29',8,1),(6,'Федорова Ольга','+375293334455','fedorova_o','employee','2025-12-27 08:57:29',8,1),(7,'Никитин Павел','+375294445566','nikitin_p','employee','2025-12-27 08:57:29',3,1),(8,'Полина Шевцова',NULL,'1345924962','manager','2025-12-27 08:58:52',NULL,1),(9,'Анна Жижейко','+375(29)391-67-16','980491377','employee','2025-12-27 09:17:07',NULL,1),(10,'Лукьяненко Сабрина','+375255158489','1472288119','employee','2025-12-27 11:27:40',8,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'business_manager'
--
/*!50003 DROP FUNCTION IF EXISTS `GetEmployeeProgress` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetEmployeeProgress`(p_user_id INT) RETURNS decimal(5,2)
    DETERMINISTIC
BEGIN
    DECLARE total_tasks INT;
    DECLARE completed_tasks INT;
    DECLARE result DECIMAL(5,2);

    SELECT COUNT(*) INTO total_tasks FROM Tasks WHERE id_employee = p_user_id;
    SELECT COUNT(*) INTO completed_tasks FROM Tasks WHERE id_employee = p_user_id AND status = 'done';

    IF total_tasks = 0 THEN
        SET result = 0;
    ELSE
        SET result = (completed_tasks / total_tasks) * 100;
    END IF;

    RETURN result;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_client_proc` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `add_client_proc`(
    IN p_full_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_telegram VARCHAR(50),
    IN p_birth_date DATE,
    IN p_segment ENUM('new','regular','vip'),
    IN p_notes TEXT,
    IN p_user_id INT
)
BEGIN
    INSERT INTO clients (full_name, phone, telegram, birth_date, segment, notes)
    VALUES (p_full_name, p_phone, p_telegram, p_birth_date, p_segment, p_notes);
    SET @last_id = LAST_INSERT_ID();
    INSERT INTO auditlogs (id_user, table_name, action, record_id, details)
    VALUES (p_user_id, 'clients', 'insert', @last_id, CONCAT('Добавлен клиент: ', p_full_name));
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_clients` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_clients`(
    IN search_name VARCHAR(255),
    IN filter_by VARCHAR(50),
    IN page INT,
    IN page_size INT
)
BEGIN
    DECLARE offset_val INT DEFAULT 0;
    SET offset_val = (page - 1) * page_size;

    IF filter_by = 'date' THEN
        SELECT * FROM clients
        WHERE full_name LIKE CONCAT('%', search_name, '%')
        ORDER BY added_date DESC
        LIMIT page_size OFFSET offset_val;

    ELSEIF filter_by = 'segment' THEN
        SELECT * FROM clients
        WHERE full_name LIKE CONCAT('%', search_name, '%')
        ORDER BY segment ASC
        LIMIT page_size OFFSET offset_val;

    ELSE
        SELECT * FROM clients
        WHERE full_name LIKE CONCAT('%', search_name, '%')
        ORDER BY added_date DESC
        LIMIT page_size OFFSET offset_val;
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-06 14:33:23
