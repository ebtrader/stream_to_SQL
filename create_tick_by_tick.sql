CREATE TABLE `tick_by_tick_all_last` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticker_id` varchar(45) NOT NULL,
  `ticker_name` varchar(45) DEFAULT NULL,
  `transaction_id` int DEFAULT NULL,
  `price` double DEFAULT NULL,
  `tick_size` int DEFAULT NULL,
  `other_attributes` varchar(100) DEFAULT NULL,
  `creation_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `time` int DEFAULT NULL,
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=703779 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contains tick by tick data at a millisecond level'