CREATE TABLE users (
                       user_id INT AUTO_INCREMENT PRIMARY KEY,
                       username VARCHAR(50) NOT NULL UNIQUE,
                       password_hash VARCHAR(255) NOT NULL,
                       email VARCHAR(100) NOT NULL UNIQUE,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
                          product_id INT AUTO_INCREMENT PRIMARY KEY,
                          name VARCHAR(100) NOT NULL,
                          description TEXT,
                          price DECIMAL(10, 2) NOT NULL,
                          stock INT NOT NULL,  -- 初始库存
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE flash_sales (
                             sale_id INT AUTO_INCREMENT PRIMARY KEY,
                             product_id INT NOT NULL,
                             start_time DATETIME NOT NULL,
                             end_time DATETIME NOT NULL,
                             total_stock INT NOT NULL,  -- 秒杀总库存
                             sold INT DEFAULT 0,         -- 已售数量
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE orders (
                        order_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        product_id INT NOT NULL,
                        sale_id INT NOT NULL,
                        order_status ENUM('PENDING', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id),
                        FOREIGN KEY (sale_id) REFERENCES flash_sales(sale_id)
);

CREATE TABLE flash_sale_records (
                                    record_id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id INT NOT NULL,
                                    sale_id INT NOT NULL,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                                    FOREIGN KEY (sale_id) REFERENCES flash_sales(sale_id),
                                    UNIQUE (user_id, sale_id)  -- 确保用户对每个秒杀活动只能参与一次
);