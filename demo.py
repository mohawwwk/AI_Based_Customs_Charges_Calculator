"""
Quick demo script to showcase the system
"""

import requests
import json

API_URL = "http://localhost:8000"

print("\n" + "="*60)
print("🌍 AI CUSTOMS CALCULATOR - DEMO")
print("="*60 + "\n")

# Demo products
demo_products = [
    {
        "name": "Headphones",
        "data": {
            "product_description": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
            "origin_country": "USA",
            "destination_country": "India",
            "price_usd": 399.0,
            "weight_kg": 0.8,
            "quantity": 1
        }
    },
    {
        "name": "Sneakers",
        "data": {
            "product_description": "Nike Air Jordan Basketball Shoes",
            "origin_country": "USA",
            "destination_country": "India",
            "price_usd": 180.0,
            "weight_kg": 1.2,
            "quantity": 1
        }
    },
    {
        "name": "Book",
        "data": {
            "product_description": "Harry Potter Complete Collection",
            "origin_country": "USA",
            "destination_country": "India",
            "price_usd": 85.0,
            "weight_kg": 2.5,
            "quantity": 1
        }
    }
]

for product in demo_products:
    print(f"📦 {product['name']}:")
    print(f"   Description: {product['data']['product_description']}")
    
    response = requests.post(
        f"{API_URL}/api/calculate",
        json=product['data']
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Classification
        classification = result['classification']
        print(f"   🤖 AI Classification: {classification['category']} ({classification['confidence']*100:.1f}% confidence)")
        
        # Charges
        charges = result['charges']
        print(f"   💰 Total Charges: ₹{charges['total_charges_inr']:,.2f} (${charges['total_charges_usd']:.2f})")
        print(f"   📊 Breakdown:")
        print(f"      - Duty: ₹{charges['duty_amount']:,.2f}")
        print(f"      - Taxes: ₹{charges['gst_amount']:,.2f}")
        print(f"      - Fees: ₹{charges['total_fees']:,.2f}")
    else:
        print("   ❌ Error calculating")
    
    print()

print("="*60)
print("✅ Demo complete! Visit http://localhost:8501 for full UI")
print("="*60 + "\n")