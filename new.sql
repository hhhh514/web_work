-- 賣家 Seller
CREATE TABLE Seller (
  seller_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  rating FLOAT DEFAULT 0.0
);

-- 商品 Product
CREATE TABLE Product (
  product_id INT PRIMARY KEY AUTO_INCREMENT,
  product_type VARCHAR(50),
  name VARCHAR(100),
  description TEXT,
  price FLOAT NOT NULL,
  stock INT DEFAULT 0,
  seller_id INT,
  FOREIGN KEY (seller_id) REFERENCES Seller(seller_id)
);

-- 顧客 Customer
CREATE TABLE Customer (
  customer_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(20),
  address TEXT
);

-- 訂單 Order
CREATE TABLE Order_Table (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  seller_id INT,
  order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_amount FLOAT DEFAULT 0.0,
  status VARCHAR(50),
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
  FOREIGN KEY (seller_id) REFERENCES Seller(seller_id)
);

-- 訂單項目 Order_Item
CREATE TABLE Order_Item (
  order_item_id INT PRIMARY KEY AUTO_INCREMENT,
  order_id INT,
  product_id INT,
  quantity INT DEFAULT 1,
  subtotal FLOAT,
  FOREIGN KEY (order_id) REFERENCES Order_Table(order_id),
  FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- 購物車 (Cart)
CREATE TABLE Cart (
  cart_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  created_date DATETIME,
  last_updated DATETIME,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- 購物車分類 (Cart Category)
CREATE TABLE Cart_Category (
  category_id INT PRIMARY KEY AUTO_INCREMENT,
  cart_id INT,
  budget DECIMAL(10, 2),
  name VARCHAR(100),
  description TEXT,
  FOREIGN KEY (cart_id) REFERENCES Cart(cart_id)
);

-- 購物車商品 (Cart Item)
CREATE TABLE Cart_Item (
  cart_item_id INT PRIMARY KEY AUTO_INCREMENT,
  cart_id INT,
  product_id INT,
  category_id INT,
  quantity INT,
  FOREIGN KEY (cart_id) REFERENCES Cart(cart_id),
  FOREIGN KEY (product_id) REFERENCES Product(product_id),
  FOREIGN KEY (category_id) REFERENCES Cart_Category(category_id)
);

-- 願望清單 WishList
CREATE TABLE WishList (
  wishlist_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- 願望清單項目 WishList_Item
CREATE TABLE WishList_Item (
  wishlist_item_id INT PRIMARY KEY AUTO_INCREMENT,
  wishlist_id INT,
  product_id INT,
  add_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (wishlist_id) REFERENCES WishList(wishlist_id),
  FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- 銷售統計 Sales_Summary
CREATE TABLE Sales_Summary (
  summary_id INT PRIMARY KEY AUTO_INCREMENT,
  seller_id INT,
  product_id INT,
  total_quantity_sold INT DEFAULT 0,
  total_revenue FLOAT DEFAULT 0.0,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (seller_id) REFERENCES Seller(seller_id),
  FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- 商品評論 Review
CREATE TABLE Review (
  review_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  product_id INT,
  rating FLOAT,
  comment TEXT,
  review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
  FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
