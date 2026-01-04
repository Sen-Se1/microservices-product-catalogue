#!/usr/bin/env python3
"""
Products Service API Test Script
Tests all CRUD operations for the Products Service
"""

import requests
import json
import uuid
import time
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """Test configuration"""
    base_url: str = "http://localhost:8001/api/v1"
    timeout: int = 10
    verbose: bool = True
    cleanup: bool = True  # Clean up test data after tests


class APIError(Exception):
    """Custom exception for API errors"""
    pass


class ProductsAPITester:
    """Comprehensive API tester for Products Service"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.created_product_ids = []
        self.test_sku_prefix = f"TEST-{int(time.time())}"
        
    def _log(self, message: str, level: str = "INFO"):
        """Log messages based on verbosity"""
        if self.config.verbose:
            if level == "INFO":
                logger.info(message)
            elif level == "ERROR":
                logger.error(message)
            elif level == "WARNING":
                logger.warning(message)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=self.config.timeout,
                **kwargs
            )
            
            self._log(f"{method} {url} - Status: {response.status_code}", "INFO")
            
            # Log response for debugging
            if self.config.verbose and response.status_code >= 400:
                self._log(f"Response: {response.text}", "ERROR")
            
            response.raise_for_status()
            
            # Return JSON if response has content
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            self._log(f"Request failed: {str(e)}", "ERROR")
            raise APIError(f"Request failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Test health endpoint"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Health Check", "INFO")
        self._log("="*50, "INFO")
        
        try:
            result = self._make_request("GET", "/health")
            if result.get("status") == "healthy":
                self._log("✅ Health check passed", "INFO")
                return True
            else:
                self._log("❌ Health check failed", "ERROR")
                return False
        except Exception as e:
            self._log(f"❌ Health check failed: {str(e)}", "ERROR")
            return False
    
    def test_create_product(self) -> Optional[str]:
        """Test creating a new product"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Create Product", "INFO")
        self._log("="*50, "INFO")
        
        test_sku = f"{self.test_sku_prefix}-001"
        product_data = {
            "name": f"Test Product {test_sku}",
            "sku": test_sku,
            "description": "This is a test product created by API tester",
            "category": "Test Category",
            "price": 99.99,
            "cost": 49.99,
            "stock_quantity": 100,
            "low_stock_threshold": 10,
            "weight_kg": 1.5,
            "dimensions_cm": "10x20x30",
            "metadata": {
                "color": "black",
                "material": "plastic",
                "test": True
            }
        }
        
        try:
            # Test 1: Create product
            self._log(f"Creating product with SKU: {test_sku}", "INFO")
            result = self._make_request("POST", "/products", json=product_data)
            
            if "id" in result:
                product_id = result["id"]
                self.created_product_ids.append(product_id)
                self._log(f"✅ Product created successfully: {product_id}", "INFO")
                
                # Verify the created product
                if result["name"] == product_data["name"] and result["sku"] == product_data["sku"]:
                    self._log("✅ Product data matches input", "INFO")
                else:
                    self._log("❌ Product data doesn't match input", "WARNING")
                
                # Test 2: Create product with duplicate SKU (should fail)
                self._log("\nTesting duplicate SKU creation...", "INFO")
                try:
                    duplicate_result = self._make_request("POST", "/products", json=product_data)
                    self._log("❌ Should have failed on duplicate SKU", "ERROR")
                    return None
                except APIError as e:
                    if "409" in str(e):
                        self._log("✅ Correctly rejected duplicate SKU", "INFO")
                    else:
                        self._log(f"❌ Wrong error for duplicate SKU: {str(e)}", "ERROR")
                
                return product_id
            else:
                self._log("❌ Product creation failed - no ID returned", "ERROR")
                return None
                
        except Exception as e:
            self._log(f"❌ Create product failed: {str(e)}", "ERROR")
            return None
    
    def test_get_products(self) -> bool:
        """Test retrieving products list"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Get Products", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Test 1: Get all products
            self._log("Getting all products...", "INFO")
            result = self._make_request("GET", "/products")
            
            if "items" in result and "total" in result:
                self._log(f"✅ Retrieved {result['total']} products", "INFO")
                self._log(f"📊 Pagination: Page {result['page']} of {result['pages']} with {result['size']} items", "INFO")
                
                # Display first few products
                if result["items"]:
                    self._log(f"📋 Sample products:", "INFO")
                    for i, product in enumerate(result["items"][:3]):
                        self._log(f"  {i+1}. {product['name']} (SKU: {product['sku']}) - ${product['price']}", "INFO")
                
                # Test 2: Get products with filters
                self._log("\nTesting filtered products...", "INFO")
                filtered_result = self._make_request("GET", "/products?category=Test Category&limit=5")
                
                if "items" in filtered_result:
                    self._log(f"✅ Filtered products retrieved: {len(filtered_result['items'])} items", "INFO")
                
                # Test 3: Get products with search
                self._log("\nTesting product search...", "INFO")
                search_result = self._make_request("GET", "/products?search=test&limit=5")
                
                if "items" in search_result:
                    self._log(f"✅ Search results: {len(search_result['items'])} items", "INFO")
                
                return True
            else:
                self._log("❌ Invalid response format", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"❌ Get products failed: {str(e)}", "ERROR")
            return False
    
    def test_get_product_by_id(self, product_id: str) -> bool:
        """Test retrieving a specific product by ID"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Get Product by ID", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Test 1: Get existing product
            self._log(f"Getting product with ID: {product_id}", "INFO")
            result = self._make_request("GET", f"/products/{product_id}")
            
            if result["id"] == product_id:
                self._log(f"✅ Product retrieved successfully", "INFO")
                self._log(f"   Name: {result['name']}", "INFO")
                self._log(f"   SKU: {result['sku']}", "INFO")
                self._log(f"   Price: ${result['price']}", "INFO")
                self._log(f"   Stock: {result['stock_quantity']}", "INFO")
                
                # Test 2: Get non-existent product (should return 404)
                self._log("\nTesting get non-existent product...", "INFO")
                fake_id = str(uuid.uuid4())
                try:
                    self._make_request("GET", f"/products/{fake_id}")
                    self._log("❌ Should have failed for non-existent product", "ERROR")
                    return False
                except APIError as e:
                    if "404" in str(e):
                        self._log("✅ Correctly returned 404 for non-existent product", "INFO")
                    else:
                        self._log(f"❌ Wrong error for non-existent product: {str(e)}", "ERROR")
                        return False
                
                # Test 3: Get product by slug
                if "slug" in result:
                    self._log(f"\nGetting product by slug: {result['slug']}", "INFO")
                    slug_result = self._make_request("GET", f"/products/slug/{result['slug']}")
                    
                    if slug_result["id"] == product_id:
                        self._log("✅ Product retrieved successfully by slug", "INFO")
                    else:
                        self._log("❌ Slug retrieval failed", "ERROR")
                        return False
                
                return True
            else:
                self._log("❌ Product ID doesn't match", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"❌ Get product by ID failed: {str(e)}", "ERROR")
            return False
    
    def test_update_product(self, product_id: str) -> bool:
        """Test updating a product"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Update Product", "INFO")
        self._log("="*50, "INFO")
        
        update_data = {
            "name": "Updated Test Product",
            "description": "This product has been updated",
            "price": 149.99,
            "stock_quantity": 50,
            "is_active": True,
            "metadata": {
                "color": "blue",
                "material": "metal",
                "updated": True
            }
        }
        
        try:
            # Test 1: Full update (PUT)
            self._log(f"Updating product {product_id}...", "INFO")
            result = self._make_request("PUT", f"/products/{product_id}", json=update_data)
            
            if result["name"] == update_data["name"] and result["price"] == update_data["price"]:
                self._log("✅ Product updated successfully", "INFO")
                self._log(f"   New name: {result['name']}", "INFO")
                self._log(f"   New price: ${result['price']}", "INFO")
                
                # Test 2: Partial update
                self._log("\nTesting partial update...", "INFO")
                partial_update = {"price": 129.99, "description": "Partially updated"}
                partial_result = self._make_request("PUT", f"/products/{product_id}", json=partial_update)
                
                if partial_result["price"] == 129.99:
                    self._log("✅ Partial update successful", "INFO")
                else:
                    self._log("❌ Partial update failed", "ERROR")
                    return False
                
                # Test 3: Update with invalid data (should fail)
                self._log("\nTesting update with invalid price...", "INFO")
                invalid_update = {"price": -10.00}
                try:
                    self._make_request("PUT", f"/products/{product_id}", json=invalid_update)
                    self._log("❌ Should have rejected invalid price", "ERROR")
                    return False
                except APIError as e:
                    if "400" in str(e):
                        self._log("✅ Correctly rejected invalid price", "INFO")
                    else:
                        self._log(f"❌ Wrong error for invalid price: {str(e)}", "ERROR")
                        return False
                
                return True
            else:
                self._log("❌ Update didn't apply correctly", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"❌ Update product failed: {str(e)}", "ERROR")
            return False
    
    def test_stock_operations(self, product_id: str) -> bool:
        """Test stock management operations"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Stock Operations", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Get current stock
            product = self._make_request("GET", f"/products/{product_id}")
            initial_stock = product["stock_quantity"]
            self._log(f"Initial stock: {initial_stock}", "INFO")
            
            # Test 1: Add stock
            self._log("\nTesting add stock operation...", "INFO")
            add_stock_data = {"quantity": 25, "operation": "add"}
            add_result = self._make_request("PATCH", f"/products/{product_id}/stock", json=add_stock_data)
            
            if add_result["stock_quantity"] == initial_stock + 25:
                self._log(f"✅ Stock added successfully: {add_result['stock_quantity']}", "INFO")
            else:
                self._log(f"❌ Stock add failed: {add_result['stock_quantity']}", "ERROR")
                return False
            
            # Test 2: Subtract stock
            self._log("\nTesting subtract stock operation...", "INFO")
            subtract_stock_data = {"quantity": 10, "operation": "subtract"}
            subtract_result = self._make_request("PATCH", f"/products/{product_id}/stock", json=subtract_stock_data)
            
            expected_stock = initial_stock + 25 - 10
            if subtract_result["stock_quantity"] == expected_stock:
                self._log(f"✅ Stock subtracted successfully: {subtract_result['stock_quantity']}", "INFO")
            else:
                self._log(f"❌ Stock subtract failed: {subtract_result['stock_quantity']}", "ERROR")
                return False
            
            # Test 3: Set stock
            self._log("\nTesting set stock operation...", "INFO")
            set_stock_data = {"quantity": 200, "operation": "set"}
            set_result = self._make_request("PATCH", f"/products/{product_id}/stock", json=set_stock_data)
            
            if set_result["stock_quantity"] == 200:
                self._log(f"✅ Stock set successfully: {set_result['stock_quantity']}", "INFO")
            else:
                self._log(f"❌ Stock set failed: {set_result['stock_quantity']}", "ERROR")
                return False
            
            # Test 4: Subtract more than available (should fail)
            self._log("\nTesting over-subtract (should fail)...", "INFO")
            over_subtract_data = {"quantity": 300, "operation": "subtract"}
            try:
                self._make_request("PATCH", f"/products/{product_id}/stock", json=over_subtract_data)
                self._log("❌ Should have failed on over-subtract", "ERROR")
                return False
            except APIError as e:
                if "400" in str(e):
                    self._log("✅ Correctly rejected over-subtract", "INFO")
                else:
                    self._log(f"❌ Wrong error for over-subtract: {str(e)}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self._log(f"❌ Stock operations failed: {str(e)}", "ERROR")
            return False
    
    def test_categories(self) -> bool:
        """Test categories endpoint"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Categories", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Create a product with unique category
            unique_category = f"Unique-Category-{int(time.time())}"
            test_product_data = {
                "name": f"Category Test Product",
                "sku": f"{self.test_sku_prefix}-CAT",
                "category": unique_category,
                "price": 49.99,
                "stock_quantity": 10
            }
            
            cat_product = self._make_request("POST", "/products", json=test_product_data)
            cat_product_id = cat_product["id"]
            self.created_product_ids.append(cat_product_id)
            
            # Test get categories
            self._log("Getting all categories...", "INFO")
            result = self._make_request("GET", "/products/categories")
            
            if isinstance(result, list):
                self._log(f"✅ Retrieved {len(result)} categories", "INFO")
                if unique_category in result:
                    self._log(f"✅ New category '{unique_category}' found in list", "INFO")
                else:
                    self._log(f"⚠️  New category not found in list", "WARNING")
                
                # Display categories
                self._log(f"📋 Categories:", "INFO")
                for i, category in enumerate(result[:10]):  # Show first 10
                    self._log(f"  {i+1}. {category}", "INFO")
                if len(result) > 10:
                    self._log(f"  ... and {len(result) - 10} more", "INFO")
                
                return True
            else:
                self._log("❌ Invalid response format for categories", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"❌ Categories test failed: {str(e)}", "ERROR")
            return False
    
    def test_low_stock(self) -> bool:
        """Test low stock endpoint"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Low Stock Products", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Create a low stock product
            low_stock_data = {
                "name": "Low Stock Test Product",
                "sku": f"{self.test_sku_prefix}-LOW",
                "category": "Test",
                "price": 19.99,
                "stock_quantity": 5,  # Low stock
                "low_stock_threshold": 10
            }
            
            low_product = self._make_request("POST", "/products", json=low_stock_data)
            low_product_id = low_product["id"]
            self.created_product_ids.append(low_product_id)
            
            # Test get low stock products
            self._log("Getting low stock products...", "INFO")
            result = self._make_request("GET", "/products/low-stock")
            
            if isinstance(result, list):
                self._log(f"✅ Retrieved {len(result)} low stock products", "INFO")
                
                # Check if our low stock product is in the list
                low_product_found = any(p["id"] == low_product_id for p in result)
                if low_product_found:
                    self._log(f"✅ Low stock product found in results", "INFO")
                else:
                    self._log(f"⚠️  Low stock product not found in results", "WARNING")
                
                # Display low stock products
                if result:
                    self._log(f"📋 Low stock products:", "INFO")
                    for i, product in enumerate(result[:5]):  # Show first 5
                        self._log(f"  {i+1}. {product['name']} - Stock: {product['stock_quantity']} (Threshold: {product['low_stock_threshold']})", "INFO")
                
                return True
            else:
                self._log("❌ Invalid response format for low stock", "ERROR")
                return False
                
        except Exception as e:
            self._log(f"❌ Low stock test failed: {str(e)}", "ERROR")
            return False
    
    def test_delete_product(self, product_id: str) -> bool:
        """Test deleting a product (soft delete)"""
        self._log("\n" + "="*50, "INFO")
        self._log("Testing Delete Product", "INFO")
        self._log("="*50, "INFO")
        
        try:
            # Test 1: Soft delete
            self._log(f"Deleting product {product_id}...", "INFO")
            self._make_request("DELETE", f"/products/{product_id}")
            self._log("✅ Delete request successful", "INFO")
            
            # Test 2: Verify product is marked inactive
            self._log("\nVerifying product is inactive...", "INFO")
            deleted_product = self._make_request("GET", f"/products/{product_id}")
            
            if deleted_product.get("is_active") == False:
                self._log("✅ Product correctly marked as inactive", "INFO")
            else:
                self._log("❌ Product still active after delete", "ERROR")
                return False
            
            # Test 3: Verify product doesn't appear in active listings
            self._log("\nChecking active product listings...", "INFO")
            active_products = self._make_request("GET", "/products")
            deleted_in_list = any(p["id"] == product_id for p in active_products["items"])
            
            if not deleted_in_list:
                self._log("✅ Deleted product not in active listings", "INFO")
            else:
                self._log("⚠️  Deleted product still in active listings", "WARNING")
            
            # Test 4: Verify product appears in inactive listings
            self._log("\nChecking inactive product listings...", "INFO")
            all_products = self._make_request("GET", "/products?include_inactive=true")
            deleted_in_all = any(p["id"] == product_id for p in all_products["items"])
            
            if deleted_in_all:
                self._log("✅ Deleted product appears when including inactive", "INFO")
            else:
                self._log("❌ Deleted product not found even when including inactive", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self._log(f"❌ Delete product test failed: {str(e)}", "ERROR")
            return False
    
    def cleanup_test_data(self):
        """Clean up all test data"""
        if not self.config.cleanup:
            return
            
        self._log("\n" + "="*50, "INFO")
        self._log("Cleaning up test data", "INFO")
        self._log("="*50, "INFO")
        
        deleted_count = 0
        for product_id in self.created_product_ids:
            try:
                # Hard delete test products (since they're test data)
                # First mark as inactive if not already
                try:
                    update_data = {"is_active": False}
                    self._make_request("PUT", f"/products/{product_id}", json=update_data)
                except:
                    pass
                
                # In a real scenario, you might have a hard delete endpoint
                # For now, we'll just log the IDs
                self._log(f"  Test product to clean up: {product_id}", "INFO")
                deleted_count += 1
                
            except Exception as e:
                self._log(f"  Failed to cleanup product {product_id}: {str(e)}", "WARNING")
        
        self._log(f"✅ Marked {deleted_count} test products for cleanup", "INFO")
        self.created_product_ids.clear()
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        self._log("\n" + "="*60, "INFO")
        self._log("STARTING COMPREHENSIVE PRODUCTS API TESTS", "INFO")
        self._log("="*60, "INFO")
        
        results = {}
        
        # Test 1: Health Check
        results["health_check"] = self.health_check()
        
        # Only continue if health check passes
        if not results["health_check"]:
            self._log("\n❌ Health check failed. Stopping tests.", "ERROR")
            return results
        
        # Test 2: Create Product
        product_id = self.test_create_product()
        results["create_product"] = product_id is not None
        
        if not product_id:
            self._log("\n❌ Create product failed. Stopping tests.", "ERROR")
            return results
        
        # Test 3: Get Products
        results["get_products"] = self.test_get_products()
        
        # Test 4: Get Product by ID
        results["get_product_by_id"] = self.test_get_product_by_id(product_id)
        
        # Test 5: Update Product
        results["update_product"] = self.test_update_product(product_id)
        
        # Test 6: Stock Operations
        results["stock_operations"] = self.test_stock_operations(product_id)
        
        # Test 7: Categories
        results["categories"] = self.test_categories()
        
        # Test 8: Low Stock
        results["low_stock"] = self.test_low_stock()
        
        # Test 9: Delete Product
        results["delete_product"] = self.test_delete_product(product_id)
        
        # Cleanup
        if self.config.cleanup:
            self.cleanup_test_data()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        self._log("\n" + "="*60, "INFO")
        self._log("TEST SUMMARY", "INFO")
        self._log("="*60, "INFO")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        self._log(f"Total Tests: {total}", "INFO")
        self._log(f"Passed: {passed}", "INFO")
        self._log(f"Failed: {total - passed}", "INFO")
        self._log(f"Success Rate: {(passed/total*100):.1f}%", "INFO")
        
        self._log("\nDetailed Results:", "INFO")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self._log(f"  {test_name}: {status}", "INFO")
        
        self._log("\n" + "="*60, "INFO")
        if passed == total:
            self._log("🎉 ALL TESTS PASSED!", "INFO")
        else:
            self._log("⚠️  SOME TESTS FAILED", "WARNING")
        self._log("="*60, "INFO")


def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Products Service API')
    parser.add_argument('--url', default='http://localhost:8001/api/v1',
                       help='Base URL of the Products Service API')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Do not clean up test data after tests')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        base_url=args.url.rstrip('/'),
        cleanup=not args.no_cleanup,
        verbose=not args.quiet,
        timeout=args.timeout
    )
    
    # Create tester and run tests
    tester = ProductsAPITester(config)
    
    try:
        results = tester.run_all_tests()
        tester.print_summary(results)
        
        # Exit with appropriate code
        if all(results.values()):
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        tester._log("\n⚠️  Tests interrupted by user", "WARNING")
        sys.exit(130)
    except Exception as e:
        tester._log(f"\n💥 Unexpected error: {str(e)}", "ERROR")
        sys.exit(2)


if __name__ == "__main__":
    main()