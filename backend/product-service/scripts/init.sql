-- Initialize Products Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop table if exists (for clean restart)
DROP TABLE IF EXISTS products CASCADE;

-- Create products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category_id VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER DEFAULT 10 CHECK (low_stock_threshold >= 0),
    discount_percentage DECIMAL(5, 2) DEFAULT 0 CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    is_active BOOLEAN DEFAULT TRUE,
    thumbnail VARCHAR(500),
    images TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_by UUID,
    product_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_products_stock ON products(stock_quantity) WHERE stock_quantity < low_stock_threshold;
CREATE INDEX idx_products_created_by ON products(created_by);
CREATE INDEX idx_products_tags ON products USING gin(tags);
CREATE INDEX idx_products_discount ON products(discount_percentage) WHERE discount_percentage > 0;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for automatic updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (do NOT specify id column - let DEFAULT handle it)
INSERT INTO products (
    name, 
    slug, 
    description, 
    sku, 
    category_id, 
    brand, 
    price, 
    discount_percentage,
    stock_quantity, 
    thumbnail, 
    images, 
    tags, 
    created_by
) VALUES
(
    'Premium Coffee Mug', 
    'premium-coffee-mug', 
    'Ceramic coffee mug with premium finish', 
    'MUG-001', 
    'kitchenware', 
    'KitchenPro', 
    24.99, 
    10.00,
    100, 
    'https://example.com/thumb/mug.jpg', 
    ARRAY['https://example.com/images/mug1.jpg', 'https://example.com/images/mug2.jpg'], 
    ARRAY['kitchen', 'ceramic', 'mug'], 
    '11111111-1111-1111-1111-111111111111'
),
(
    'Wireless Mouse', 
    'wireless-mouse', 
    'Ergonomic wireless mouse with 2.4GHz receiver', 
    'MOUSE-001', 
    'electronics', 
    'TechBrand', 
    39.99, 
    0,
    50, 
    'https://example.com/thumb/mouse.jpg', 
    ARRAY['https://example.com/images/mouse1.jpg', 'https://example.com/images/mouse2.jpg'], 
    ARRAY['electronics', 'wireless', 'mouse'], 
    '22222222-2222-2222-2222-222222222222'
),
(
    'Organic Cotton T-Shirt', 
    'organic-cotton-t-shirt', 
    '100% organic cotton t-shirt', 
    'TSHIRT-001', 
    'apparel', 
    'EcoWear', 
    29.99, 
    15.00,
    200, 
    'https://example.com/thumb/tshirt.jpg', 
    ARRAY['https://example.com/images/tshirt1.jpg', 'https://example.com/images/tshirt2.jpg'], 
    ARRAY['apparel', 'organic', 'cotton'], 
    '33333333-3333-3333-3333-333333333333'
)
ON CONFLICT (sku) DO NOTHING;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON TABLE products TO products_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO products_user;

-- Create comments for documentation
COMMENT ON TABLE products IS 'Stores product information for the e-commerce system';
COMMENT ON COLUMN products.slug IS 'URL-friendly version of product name for SEO';
COMMENT ON COLUMN products.thumbnail IS 'URL to thumbnail/small preview image';
COMMENT ON COLUMN products.images IS 'Array of URLs to full-size product images';
COMMENT ON COLUMN products.tags IS 'Array of tags for categorization and search';
COMMENT ON COLUMN products.created_by IS 'ID of user who created the product';
COMMENT ON COLUMN products.product_metadata IS 'Flexible JSON field for additional product attributes';
COMMENT ON COLUMN products.discount_percentage IS 'Percentage discount (0-100)';

-- Verify the data was inserted
SELECT COUNT(*) as product_count FROM products;