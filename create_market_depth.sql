CREATE TABLE javeddb.updatemarketdepth (
  `id` int NOT NULL AUTO_INCREMENT,
  `ReqId` int NOT NULL,
  `POSITION` int NOT NULL,
  `Operation` int NOT NULL,
  `Side` int NOT NULL,
  `Price` double DEFAULT NULL,
  `SIZE` int NOT NULL,
  `timestamp` varchar(100) NOT NULL,
  UNIQUE KEY `id_unique` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci