# CREATE TABLE categories (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL UNIQUE,
#     description TEXT,
#     slug VARCHAR(100) UNIQUE,
#     image VARCHAR(500),
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE INDEX idx_categories_slug ON categories(slug);