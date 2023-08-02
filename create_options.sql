CREATE TABLE javeddb.options (
  `id` int NOT NULL AUTO_INCREMENT,
  `ReqId` int NOT NULL,
  `TickType` int NOT NULL,
  `Price` double DEFAULT NULL,
  UNIQUE KEY `id_unique` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci