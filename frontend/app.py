import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Customs Calculator",
    page_icon="🌍",
    layout="wide"
)

# API base URL
API_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🌍 AI Customs Calculator</div>', unsafe_allow_html=True)
st.markdown("### Calculate customs duties for international e-commerce orders")
st.markdown("---")

# Check API health
def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

# Show API status
api_status, health_data = check_api_health()

if not api_status:
    st.error("⚠️ **API Server is not running!**")
    st.info("Please start the FastAPI server:")
    st.code("cd backend\npython main.py", language="bash")
    st.stop()
else:
    # Show health status in sidebar
    with st.sidebar:
        st.success("✅ API Connected")
        if health_data:
            st.json(health_data)

# Main content
st.subheader("📝 Enter Order Details")

# Create input form
col1, col2 = st.columns(2)

with col1:
    product_description = st.text_area(
        "Product Description",
        placeholder="e.g., Sony WH-1000XM5 Wireless Headphones",
        help="Describe the product in detail",
        height=100
    )
    
    origin = st.selectbox(
        "Origin Country",
        ["USA", "China", "UK", "Germany"],
        help="Country where the product is shipping from"
    )
    
    destination = st.selectbox(
        "Destination Country",
        ["India"],
        help="Country where the product is shipping to"
    )

with col2:
    price_usd = st.number_input(
        "Price (USD)",
        min_value=0.0,
        value=100.0,
        step=1.0,
        help="Product price in US Dollars"
    )
    
    weight_kg = st.number_input(
        "Weight (kg)",
        min_value=0.1,
        value=1.0,
        step=0.1,
        help="Product weight in kilograms"
    )
    
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=1,
        step=1,
        help="Number of items"
    )

# Example products
st.markdown("---")
st.subheader("🎯 Try an Example")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📱 Example: Headphones", use_container_width=True):
        st.session_state.example = {
            'description': "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
            'origin': "USA",
            'price': 399.0,
            'weight': 0.8,
            'quantity': 1
        }
        st.rerun()

with col2:
    if st.button("👟 Example: Sneakers", use_container_width=True):
        st.session_state.example = {
            'description': "Nike Air Jordan Basketball Shoes",
            'origin': "USA",
            'price': 180.0,
            'weight': 1.2,
            'quantity': 1
        }
        st.rerun()

with col3:
    if st.button("📚 Example: Book", use_container_width=True):
        st.session_state.example = {
            'description': "Python Programming for Beginners Textbook",
            'origin': "USA",
            'price': 45.0,
            'weight': 0.6,
            'quantity': 1
        }
        st.rerun()

# Apply example if selected
if 'example' in st.session_state:
    product_description = st.session_state.example['description']
    origin = st.session_state.example['origin']
    price_usd = st.session_state.example['price']
    weight_kg = st.session_state.example['weight']
    quantity = st.session_state.example['quantity']
    del st.session_state.example

st.markdown("---")

# Calculation options
col1, col2 = st.columns(2)

with col1:
    calculate_type = st.radio(
        "Choose calculation type:",
        ["Standard Calculation", "With PDF Report"],
        help="PDF report generates a downloadable document"
    )

with col2:
    st.write("")  # Spacer

# Calculate button
if st.button("🔍 Calculate Customs Charges", type="primary", use_container_width=True):
    if not product_description:
        st.error("⚠️ Please enter a product description")
    else:
        # Prepare request data
        request_data = {
            "product_description": product_description,
            "origin_country": origin,
            "destination_country": destination,
            "price_usd": price_usd,
            "weight_kg": weight_kg,
            "quantity": quantity
        }
        
        # Show loading
        with st.spinner("🤖 AI is analyzing your product and calculating charges..."):
            try:
                # Make API call
                if calculate_type == "With PDF Report":
                    endpoint = f"{API_URL}/api/calculate/pdf"
                else:
                    endpoint = f"{API_URL}/api/calculate"
                
                response = requests.post(
                    endpoint,
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Success message
                    st.success("✅ Customs charges calculated successfully!")
                    
                    # Order ID
                    st.markdown(f'<div class="info-box"><b>Order ID:</b> <code>{result["order_id"]}</code> | <b>Timestamp:</b> {result.get("timestamp", "N/A")}</div>', unsafe_allow_html=True)
                    
                    # Display results
                    st.markdown("---")
                    
                    # Two columns for classification and pricing
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🤖 AI Classification")
                        
                        classification = result.get('classification', {})
                        
                        st.metric(
                            label="Category",
                            value=classification.get('category', 'N/A')
                        )
                        
                        st.metric(
                            label="HS Code",
                            value=classification.get('hs_code', 'N/A')
                        )
                        
                        confidence = classification.get('confidence', 0)
                        st.metric(
                            label="AI Confidence",
                            value=f"{confidence*100:.1f}%"
                        )
                        
                        # Progress bar
                        st.progress(confidence)
                        
                        if classification.get('requires_manual_review', False):
                            st.warning("⚠️ Low confidence - Manual review recommended")
                        else:
                            st.success("✓ High confidence - Classification reliable")
                        
                        # Keywords
                        with st.expander("🔍 Keywords Detected"):
                            keywords = classification.get('keywords', [])
                            if keywords:
                                st.write("**Matched keywords:** " + ", ".join(keywords))
                            else:
                                st.write("No specific keywords matched")
                    
                    with col2:
                        st.subheader("💰 Pricing Summary")
                        
                        charges = result.get('charges', {})
                        
                        st.metric(
                            label="Base Price",
                            value=f"${price_usd * quantity:.2f}",
                            delta=f"₹{charges.get('base_price_inr', 0):,.2f} @ ₹{charges.get('exchange_rate', 83)}/USD"
                        )
                        
                        st.metric(
                            label="Total Customs Charges",
                            value=f"₹{charges.get('total_charges_inr', 0):,.2f}",
                            delta=f"${charges.get('total_charges_usd', 0):.2f} USD",
                            delta_color="off"
                        )
                        
                        # Percentage of original price
                        if charges.get('base_price_inr', 0) > 0:
                            charge_percentage = (charges.get('total_charges_inr', 0) / charges.get('base_price_inr', 1)) * 100
                            st.metric(
                                label="Charges as % of Price",
                                value=f"{charge_percentage:.1f}%"
                            )
                    
                    # Detailed breakdown
                    st.markdown("---")
                    st.subheader("📊 Detailed Breakdown")
                    
                    # Create breakdown table
                    breakdown_data = {
                        'Charge Type': [
                            'Customs Duty',
                            'GST (Goods & Services Tax)',
                            'Customs Handling Fee',
                            'Port Charges',
                            'Documentation Fee',
                            '**TOTAL**'
                        ],
                        'Rate/Method': [
                            f"{charges.get('duty_rate', 0)*100:.1f}%",
                            f"{charges.get('gst_rate', 0)*100:.1f}%",
                            'Flat Fee',
                            f"₹50/kg × {weight_kg * quantity:.1f}kg",
                            'Flat Fee',
                            ''
                        ],
                        'Amount (INR)': [
                            f"₹{charges.get('duty_amount', 0):,.2f}",
                            f"₹{charges.get('gst_amount', 0):,.2f}",
                            f"₹{charges.get('customs_handling', 0):,.2f}",
                            f"₹{charges.get('port_charges', 0):,.2f}",
                            f"₹{charges.get('documentation', 0):,.2f}",
                            f"**₹{charges.get('total_charges_inr', 0):,.2f}**"
                        ],
                        'Regulation': [
                            charges.get('duty_regulation', 'N/A')[:50] + '...',
                            'GST Act 2017, Notification 01/2024',
                            'CBIC Circular 15/2024',
                            'Port Trust Act 2023, Schedule A',
                            'CBIC Circular 08/2024',
                            f'**(${charges.get("total_charges_usd", 0):.2f} USD)**'
                        ]
                    }
                    
                    df = pd.DataFrame(breakdown_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Summary metrics
                    st.markdown("---")
                    st.subheader("💵 Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Duty", f"₹{charges.get('duty_amount', 0):,.2f}")
                    with col2:
                        st.metric("Total Taxes", f"₹{charges.get('gst_amount', 0):,.2f}")
                    with col3:
                        st.metric("Total Fees", f"₹{charges.get('total_fees', 0):,.2f}")
                    with col4:
                        st.metric("Grand Total", f"₹{charges.get('total_charges_inr', 0):,.2f}")
                    
                    # PDF download if available
                    if 'pdf' in result and result['pdf'].get('generated'):
                        st.markdown("---")
                        st.subheader("📥 Download Report")
                        
                        pdf_url = f"{API_URL}{result['pdf']['download_url']}"
                        
                        st.success("✅ PDF report generated successfully!")
                        st.markdown(f"**Download:** [📄 {result['pdf']['filename']}]({pdf_url})")
                        
                        st.info("💡 Click the link above to download your customs calculation report")
                    
                    # Additional info
                    st.markdown("---")
                    st.info("""
                    **📋 Important Notes:**
                    - All calculations are based on current customs regulations and tax rates
                    - This is an AI-assisted estimate. Final charges may vary slightly
                    - All regulations cited are traceable and audit-ready
                    - Exchange rates are updated daily (current rate: ₹83/USD)
                    - For official customs clearance, please consult a licensed customs broker
                    """)
                    
                    # Processing time
                    st.caption(f"⏱️ Processed in {result.get('processing_time_seconds', 0)} seconds | 🤖 AI Classification + 📊 Rule-Based Calculation")
                
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to API. Make sure the backend is running.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
# Sidebar - System Status
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 System Status")
    
    try:
        perf_response = requests.get(f"{API_URL}/api/performance", timeout=5)
        if perf_response.status_code == 200:
            perf = perf_response.json()
            
            # System metrics
            st.metric("CPU Usage", f"{perf['system']['cpu_usage_percent']:.1f}%")
            st.metric("Memory Usage", f"{perf['system']['memory']['percent']:.1f}%")
            
            # Database stats
            st.metric("Total Rules", perf['database']['total_rules'])
            st.metric("Calculations Today", perf['database']['total_calculations'])
            
            # Model info
            with st.expander("🤖 ML Model Info"):
                st.write(f"**Type:** {perf['model']['type']}")
                st.write(f"**Accuracy:** {perf['model']['accuracy']}")
                st.write(f"**Vocabulary:** {perf['model']['vocabulary_size']} words")
    except:
        st.info("Performance stats unavailable")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI-Assisted Customs Charge Calculator | Built for PBL Project 2024</p>
    <p>Team: Mohak, Mohnish, Nigel, Nitesh | Guided by: Dr. Shewtambhari Chiwhane</p>
</div>
""", unsafe_allow_html=True)