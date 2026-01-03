#!/usr/bin/env python3
"""
Test Analytics Service API endpoints
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime, timedelta
import uuid

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8003"
API_PREFIX = "/api/v1/analytics"

# Test JWT token (in production, get this from User Service)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE5MDAwMDAwMDB9.test-signature"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbi11c2VyIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxOTAwMDAwMDAwfQ.admin-test-signature"

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_result(endpoint, method, success, response_code=None):
    status = "✅ PASS" if success else "❌ FAIL"
    code_info = f" ({response_code})" if response_code else ""
    print(f"{status} {method} {endpoint}{code_info}")

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {TEST_TOKEN}",
            "Content-Type": "application/json"
        }
        self.admin_headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }
        self.results = {}
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        endpoint = "/health"
        method = "GET"
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
            success = response.status_code == 200 and response.json().get("status") == "healthy"
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                print(f"   Service: {data.get('service')}")
                print(f"   Redis: {data.get('redis', {}).get('status')}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_track_product_view(self):
        """Test product view tracking"""
        endpoint = f"{API_PREFIX}/track/view"
        method = "POST"
        
        payload = {
            "product_id": str(uuid.uuid4()),
            "session_id": f"test_session_{uuid.uuid4().hex[:8]}",
            "duration_seconds": 45,
            "device_info": {
                "browser": "Chrome",
                "os": "Windows 10",
                "screen_resolution": "1920x1080"
            },
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            
            success = response.status_code == 201
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                print(f"   Tracked view ID: {data.get('id')}")
                print(f"   Product ID: {data.get('product_id')}")
            else:
                print(f"   Error: {response.text}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_track_sale(self):
        """Test sale tracking"""
        endpoint = f"{API_PREFIX}/track/sale"
        method = "POST"
        
        payload = {
            "order_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "amount": 149.99,
            "quantity": 2,
            "sale_date": datetime.now().isoformat(),
            "payment_method": "credit_card",
            "region": "US-CA"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            
            success = response.status_code == 201
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                print(f"   Sale tracked: {data.get('id')}")
                print(f"   Order ID: {payload['order_id']}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_generate_sales_report(self):
        """Test sales report generation"""
        endpoint = f"{API_PREFIX}/sales"
        method = "POST"
        
        payload = {
            "start_date": (datetime.now() - timedelta(days=7)).date().isoformat(),
            "end_date": datetime.now().date().isoformat(),
            "group_by": "day"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            
            success = response.status_code == 200
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                items = data.get("items", [])
                summary = data.get("summary", {})
                
                print(f"   Report period: {summary.get('period', {}).get('start_date')} to {summary.get('period', {}).get('end_date')}")
                print(f"   Total sales: ${summary.get('total_sales', 0):.2f}")
                print(f"   Total orders: {summary.get('total_orders', 0)}")
                print(f"   Items returned: {len(items)}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_generate_product_views_report(self):
        """Test product views report"""
        endpoint = f"{API_PREFIX}/product-views"
        method = "POST"
        
        payload = {
            "start_date": (datetime.now() - timedelta(days=30)).date().isoformat(),
            "end_date": datetime.now().date().isoformat(),
            "limit": 5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            
            success = response.status_code == 200
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                items = data.get("items", [])
                period = data.get("period", {})
                
                print(f"   Period: {period.get('start_date')} to {period.get('end_date')}")
                print(f"   Products returned: {len(items)}")
                
                if items:
                    top_product = items[0]
                    print(f"   Top product views: {top_product.get('view_count')}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_realtime_metrics(self):
        """Test real-time metrics endpoint"""
        endpoint = f"{API_PREFIX}/realtime-metrics"
        method = "GET"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                timeout=5
            )
            
            success = response.status_code == 200
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                print(f"   Active users: {data.get('active_users')}")
                print(f"   Today's views: {data.get('today_views')}")
                print(f"   Today's sales: ${data.get('today_sales', 0):.2f}")
                print(f"   Conversion rate: {data.get('conversion_rate', 0)}%")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_user_activities_admin(self):
        """Test user activities endpoint (admin only)"""
        endpoint = f"{API_PREFIX}/user-activities"
        method = "GET"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.admin_headers,
                timeout=5
            )
            
            # Should work with admin token
            success = response.status_code == 200
            
            print_result(endpoint, method, success, response.status_code)
            
            if success:
                data = response.json()
                print(f"   Activities returned: {len(data)}")
                if data:
                    print(f"   First activity type: {data[0].get('activity_type')}")
            
            return success
            
        except Exception as e:
            print_result(endpoint, method, False)
            print(f"   Error: {e}")
            return False
    
    def test_user_activities_non_admin(self):
        """Test user activities endpoint without admin privileges"""
        endpoint = f"{API_PREFIX}/user-activities"
        method = "GET"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,  # Non-admin token
                timeout=5
            )
            
            # Should fail with 403 Forbidden for non-admin
            success = response.status_code == 403
            
            print_result(f"{endpoint} (non-admin)", method, success, response.status_code)
            
            if success:
                print("   ✓ Correctly denied access to non-admin user")
            else:
                print(f"   Unexpected response: {response.status_code}")
            
            return success
            
        except Exception as e:
            print_result(f"{endpoint} (non-admin)", method, False)
            print(f"   Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print_header("ANALYTICS SERVICE API TEST SUITE")
        print(f"Base URL: {self.base_url}")
        
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Track Product View", self.test_track_product_view),
            ("Track Sale", self.test_track_sale),
            ("Sales Report", self.test_generate_sales_report),
            ("Product Views Report", self.test_generate_product_views_report),
            ("Real-time Metrics", self.test_realtime_metrics),
            ("User Activities (Admin)", self.test_user_activities_admin),
            ("User Activities (Non-admin)", self.test_user_activities_non_admin),
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            try:
                result = test_func()
                self.results[test_name] = result
            except Exception as e:
                print(f"   ❌ Test error: {e}")
                self.results[test_name] = False
        
        # Print summary
        print_header("API TEST SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        return all(self.results.values())

def main():
    """Main test runner"""
    
    # Check if service is running
    print("Checking if service is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Service is running")
        else:
            print("❌ Service not responding properly")
            print("Starting service first...")
            print("\nRun in a separate terminal:")
            print("  cd analytics-service")
            print("  source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
            print("  python -m app.main")
            print("\nThen run this test again.")
            return 1
    except requests.ConnectionError:
        print("❌ Service is not running on port 8003")
        print("\nTo start the service:")
        print("1. Activate virtual environment:")
        print("   source venv/bin/activate  # Linux/macOS")
        print("   venv\\Scripts\\activate   # Windows")
        print("\n2. Start the service:")
        print("   python -m app.main")
        print("\n3. Then run this test in another terminal")
        return 1
    
    # Run API tests
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL API TESTS PASSED!")
        print("\nYou can now:")
        print("1. Access API documentation: http://localhost:8003/docs")
        print("2. Test manually with curl or Postman")
        print("3. Integrate with your frontend applications")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nTroubleshooting tips:")
        print("1. Check if database services are running")
        print("2. Verify .env configuration")
        print("3. Check service logs for errors")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)