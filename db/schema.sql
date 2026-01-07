-- Cart
CREATE TABLE IF NOT EXISTS cart_items (
  id UUID PRIMARY KEY,
  user_id UUID,
  product_id UUID,
  name TEXT,
  weight TEXT,
  price NUMERIC,
  quantity INT,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Addresses
CREATE TABLE IF NOT EXISTS addresses (
  id UUID PRIMARY KEY,
  user_id UUID,
  name TEXT,
  mobile VARCHAR(10),
  address_line1 TEXT,
  address_line2 TEXT,
  city TEXT,
  pincode TEXT,
  latitude FLOAT,
  longitude FLOAT,
  is_default BOOLEAN DEFAULT FALSE
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY,
  user_id UUID,
  total_amount NUMERIC,
  payment_method TEXT,
  payment_status TEXT,
  order_status TEXT,
  address_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
  id UUID PRIMARY KEY,
  order_id UUID,
  product_id UUID,
  name TEXT,
  weight TEXT,
  price NUMERIC,
  quantity INT
);

