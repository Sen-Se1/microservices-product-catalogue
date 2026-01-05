# CREATE TABLE product_reviews (
#     id SERIAL PRIMARY KEY,
#     product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
#     user_id VARCHAR(100), -- Reference to MongoDB user_id
#     rating INTEGER CHECK (rating >= 1 AND rating <= 5),
#     comment TEXT,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
# );

# CREATE INDEX idx_reviews_product ON product_reviews(product_id);
# CREATE INDEX idx_reviews_user ON product_reviews(user_id);
# CREATE INDEX idx_reviews_rating ON product_reviews(rating);