import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

API_URL = "http://localhost:8000"

def print_test(name, passed):
    """Print test result with colors"""
    if passed:
        print(f"{Fore.GREEN}✓ {name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ {name}{Style.RESET_ALL}")

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        passed = response.status_code == 200 and response.json()['status'] == 'healthy'
        print_test("Health Check", passed)
        return passed
    except Exception as e:
        print_test(f"Health Check - Error: {e}", False)
        return False

def test_classification():
    """Test classification endpoint"""
    try:
        test_cases = [
            ("Sony WH-1000XM5 Wireless Headphones", "Electronics"),
            ("Nike Air Jordan Basketball Shoes", "Clothing"),
            ("Harry Potter Complete Book Collection", "Books"),
            ("LEGO Star Wars Building Set", "Toys")
        ]
        
        all_passed = True
        for description, expected_category in test_cases:
            response = requests.post(
                f"{API_URL}/api/classify",
                json={"description": description},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                passed = result['category'] == expected_category and result['confidence'] > 0.7
                print_test(f"Classify: {description[:30]}... → {expected_category}", passed)
                all_passed = all_passed and passed
            else:
                print_test(f"Classify: {description[:30]}...", False)
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_test(f"Classification - Error: {e}", False)
        return False

def test_calculation():
    """Test calculation endpoint"""
    try:
        request_data = {
            "product_description": "Sony WH-1000XM5 Wireless Headphones",
            "origin_country": "USA",
            "destination_country": "India",
            "price_usd": 399.0,
            "weight_kg": 0.8,
            "quantity": 1
        }
        
        response = requests.post(
            f"{API_URL}/api/calculate",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            passed = (
                'classification' in result and
                'charges' in result and
                result['charges']['total_charges_inr'] > 0
            )
            print_test("Calculate Customs Charges", passed)
            return passed
        else:
            print_test("Calculate Customs Charges", False)
            return False
    except Exception as e:
        print_test(f"Calculation - Error: {e}", False)
        return False

def test_pdf_generation():
    """Test PDF generation"""
    try:
        request_data = {
            "product_description": "Apple MacBook Pro M3",
            "origin_country": "USA",
            "destination_country": "India",
            "price_usd": 2499.0,
            "weight_kg": 1.6,
            "quantity": 1
        }
        
        response = requests.post(
            f"{API_URL}/api/calculate/pdf",
            json=request_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            passed = 'pdf' in result and result['pdf']['generated'] == True
            print_test("PDF Generation", passed)
            return passed
        else:
            print_test("PDF Generation", False)
            return False
    except Exception as e:
        print_test(f"PDF Generation - Error: {e}", False)
        return False

def test_admin_endpoints():
    """Test admin endpoints"""
    try:
        # Get all rules
        response = requests.get(f"{API_URL}/admin/rules", timeout=5)
        get_passed = response.status_code == 200 and len(response.json()) > 0
        print_test("Admin: Get All Rules", get_passed)
        
        # Get statistics
        response = requests.get(f"{API_URL}/admin/stats", timeout=5)
        stats_passed = response.status_code == 200
        print_test("Admin: Get Statistics", stats_passed)
        
        # Get audit log
        response = requests.get(f"{API_URL}/admin/audit-log?limit=10", timeout=5)
        audit_passed = response.status_code == 200
        print_test("Admin: Get Audit Log", audit_passed)
        
        return get_passed and stats_passed and audit_passed
    except Exception as e:
        print_test(f"Admin Endpoints - Error: {e}", False)
        return False

def test_error_handling():
    """Test error handling"""
    try:
        # Test with missing fields
        response = requests.post(
            f"{API_URL}/api/calculate",
            json={},
            timeout=5
        )
        passed = response.status_code == 422  # Validation error
        print_test("Error Handling: Missing Fields", passed)
        return passed
    except Exception as e:
        print_test(f"Error Handling - Error: {e}", False)
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}🧪 RUNNING API TESTS{Style.RESET_ALL}")
    print("="*60 + "\n")
    
    results = {
        "Health Check": test_health_endpoint(),
        "Classification": test_classification(),
        "Calculation": test_calculation(),
        "PDF Generation": test_pdf_generation(),
        "Admin Endpoints": test_admin_endpoints(),
        "Error Handling": test_error_handling()
    }
    
    print("\n" + "="*60)
    print(f"{Fore.CYAN}📊 TEST SUMMARY{Style.RESET_ALL}")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {total - passed}{Style.RESET_ALL}")
    print(f"\nSuccess Rate: {passed/total*100:.1f}%\n")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 ALL TESTS PASSED!{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}⚠️ Some tests failed. Check the output above.{Style.RESET_ALL}\n")

if __name__ == "__main__":
    # Install colorama if needed
    try:
        import colorama
    except ImportError:
        print("Installing colorama for colored output...")
        import subprocess
        subprocess.run(["pip", "install", "colorama"])
        from colorama import init, Fore, Style
        init(autoreset=True)
    
    run_all_tests()