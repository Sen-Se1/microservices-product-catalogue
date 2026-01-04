-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    cost DECIMAL(10, 2) CHECK (cost >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER DEFAULT 10 CHECK (low_stock_threshold >= 0),
    weight_kg DECIMAL(5, 2) CHECK (weight_kg >= 0),
    dimensions_cm VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_products_stock ON products(stock_quantity) WHERE stock_quantity < low_stock_threshold;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO products (name, slug, description, sku, category, price, cost, stock_quantity, weight_kg, dimensions_cm, image_url) VALUES
('Premium Coffee Mug', 'premium-coffee-mug', 'Ceramic coffee mug with premium finish', 'MUG-001', 'Kitchenware', 24.99, 8.50, 100, 0.35, '10x10x12', 'https://example.com/mug.jpg'),
('Wireless Mouse', 'wireless-mouse', 'Ergonomic wireless mouse with 2.4GHz receiver', 'MOUSE-001', 'Electronics', 39.99, 15.00, 50, 0.12, '10x6x3', 'https://example.com/mouse.jpg'),
('Organic Cotton T-Shirt', 'organic-cotton-t-shirt', '100% organic cotton t-shirt', 'TSHIRT-001', 'Apparel', 29.99, 12.00, 200, 0.25, 'SIZE:M', 'https://example.com/tshirt.jpg')
ON CONFLICT (sku) DO NOTHING;