import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Customs Admin Dashboard",
    page_icon="🔧",
    layout="wide"
)

# API base URL
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #e74c3c;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🔧 Customs Admin Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Manage customs rules and view system statistics")
st.markdown("---")

# Simple authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔒 Admin Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if password == "admin123":  # Simple password for demo
                st.session_state.authenticated = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
        
        st.info("💡 Demo password: **admin123**")
    
    st.stop()

# Logout button
if st.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

# Tabs
tabs = st.tabs(["📋 View Rules", "➕ Add Rule", "✏️ Update Rule", "📊 Statistics", "📜 Audit Log"])

# TAB 1: View Rules
with tabs[0]:
    st.subheader("Current Customs Rules")
    
    try:
        response = requests.get(f"{API_URL}/admin/rules", timeout=10)
        
        if response.status_code == 200:
            rules = response.json()
            
            if rules:
                # Convert to DataFrame
                df = pd.DataFrame(rules)
                
                # Select and rename columns
                display_columns = ['id', 'origin_country', 'destination_country', 
                                 'product_category', 'hs_code', 'base_duty_rate', 
                                 'gst_rate', 'regulation_reference']
                
                df = df[display_columns]
                
                # Format rates as percentages
                df['base_duty_rate'] = df['base_duty_rate'].apply(lambda x: f"{x*100:.1f}%")
                df['gst_rate'] = df['gst_rate'].apply(lambda x: f"{x*100:.1f}%")
                
                # Rename columns
                df.columns = ['ID', 'Origin', 'Destination', 'Category', 'HS Code', 
                            'Duty Rate', 'GST Rate', 'Regulation']
                
                # Display
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.success(f"✅ Found {len(rules)} customs rules")
            else:
                st.warning("No rules found in database")
        else:
            st.error(f"Error fetching rules: {response.json().get('detail', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB 2: Add Rule
with tabs[1]:
    st.subheader("Add New Customs Rule")
    
    with st.form("add_rule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            origin = st.selectbox("Origin Country", ["USA", "China", "UK", "Germany", "Japan"])
            destination = st.selectbox("Destination Country", ["India", "UAE", "Singapore"])
            category = st.selectbox("Product Category", ["Electronics", "Clothing", "Books", "Toys"])
        
        with col2:
            hs_code = st.text_input("HS Code", placeholder="e.g., 8518.30.00")
            duty_rate = st.slider("Duty Rate (%)", 0.0, 50.0, 10.0, 0.5)
            gst_rate = st.slider("GST Rate (%)", 0.0, 30.0, 18.0, 0.5)
        
        regulation = st.text_input(
            "Regulation Reference",
            placeholder="e.g., India Customs Tariff Act 2024, Schedule II"
        )
        
        notes = st.text_area("Notes", placeholder="Additional information...")
        
        submitted = st.form_submit_button("Add Rule", use_container_width=True)
        
        if submitted:
            if not hs_code or not regulation:
                st.error("Please fill in all required fields")
            else:
                try:
                    request_data = {
                        "origin_country": origin,
                        "destination_country": destination,
                        "product_category": category,
                        "hs_code": hs_code,
                        "base_duty_rate": duty_rate / 100,
                        "gst_rate": gst_rate / 100,
                        "regulation_reference": regulation,
                        "notes": notes
                    }
                    
                    response = requests.post(
                        f"{API_URL}/admin/rules",
                        json=request_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ Rule added successfully!")
                        st.balloons()
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# TAB 3: Update Rule
with tabs[2]:
    st.subheader("Update Existing Rule")
    
    # Select rule to update
    rule_id = st.number_input("Rule ID to Update", min_value=1, step=1, value=1)
    
    if st.button("Load Rule", use_container_width=True):
        try:
            response = requests.get(f"{API_URL}/admin/rules/{rule_id}", timeout=10)
            
            if response.status_code == 200:
                st.session_state.rule_to_update = response.json()
                st.success(f"✅ Loaded rule ID {rule_id}")
            else:
                st.error(f"Rule ID {rule_id} not found")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if 'rule_to_update' in st.session_state:
        rule = st.session_state.rule_to_update
        
        st.info(f"**Updating:** {rule['product_category']} | {rule['origin_country']} → {rule['destination_country']}")
        
        with st.form("update_rule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_duty_rate = st.slider(
                    "New Duty Rate (%)",
                    0.0, 50.0,
                    float(rule['base_duty_rate']) * 100,
                    0.5
                )
            
            with col2:
                new_gst_rate = st.slider(
                    "New GST Rate (%)",
                    0.0, 30.0,
                    float(rule['gst_rate']) * 100,
                    0.5
                )
            
            new_regulation = st.text_input(
                "Regulation Reference",
                value=rule['regulation_reference']
            )
            
            new_notes = st.text_area(
                "Notes",
                value=rule.get('notes', '')
            )
            
            reason = st.text_area(
                "Reason for Change (for audit trail)",
                placeholder="e.g., Government notification #05/2024"
            )
            
            submitted = st.form_submit_button("Update Rule", use_container_width=True)
            
            if submitted:
                if not reason:
                    st.error("Please provide a reason for the change")
                else:
                    try:
                        request_data = {
                            "base_duty_rate": new_duty_rate / 100,
                            "gst_rate": new_gst_rate / 100,
                            "regulation_reference": new_regulation,
                            "notes": f"{new_notes}\n[Updated: {datetime.now().strftime('%Y-%m-%d')} - {reason}]"
                        }
                        
                        response = requests.put(
                            f"{API_URL}/admin/rules/{rule_id}",
                            json=request_data,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Rule updated successfully!")
                            st.info("💡 Changes take effect immediately. No code deployment needed!")
                            del st.session_state.rule_to_update
                            st.balloons()
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# TAB 4: Statistics
with tabs[3]:
    st.subheader("System Statistics")
    
    try:
        response = requests.get(f"{API_URL}/admin/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data['statistics']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rules", stats['total_rules'])
            
            with col2:
                st.metric("Total Calculations", stats['total_calculations'])
            
            with col3:
                st.metric("Average Charges", f"₹{stats['average_charges_inr']:,.0f}")
            
            with col4:
                routes = len(stats['rules_by_route'])
                st.metric("Active Routes", routes)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Rules by Route")
                if stats['rules_by_route']:
                    route_df = pd.DataFrame(stats['rules_by_route'])
                    route_df['route'] = route_df['origin_country'] + ' → ' + route_df['destination_country']
                    st.bar_chart(route_df.set_index('route')['count'])
            
            with col2:
                st.subheader("Calculations by Category")
                if stats['calculations_by_category']:
                    calc_df = pd.DataFrame(stats['calculations_by_category'])
                    st.bar_chart(calc_df.set_index('classified_category')['count'])
        
        else:
            st.error("Error fetching statistics")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB 5: Audit Log
with tabs[4]:
    st.subheader("Recent Calculations (Audit Log)")
    
    limit = st.slider("Number of records to show", 10, 100, 50, 10)
    
    try:
        response = requests.get(f"{API_URL}/admin/audit-log?limit={limit}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logs = data['logs']
            
            if logs:
                # Convert to DataFrame
                df = pd.DataFrame(logs)
                
                # Select columns
                display_columns = ['order_id', 'timestamp', 'classified_category', 
                                 'origin_country', 'destination_country', 
                                 'base_price_usd', 'total_charges_inr']
                
                df = df[display_columns]
                
                # Rename columns
                df.columns = ['Order ID', 'Timestamp', 'Category', 'Origin', 
                            'Destination', 'Price (USD)', 'Charges (INR)']
                
                # Format
                df['Price (USD)'] = df['Price (USD)'].apply(lambda x: f"${x:,.2f}")
                df['Charges (INR)'] = df['Charges (INR)'].apply(lambda x: f"₹{x:,.2f}")
                
                # Display
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.success(f"✅ Showing {len(logs)} recent calculations")
            else:
                st.info("No calculations found in audit log")
        
        else:
            st.error("Error fetching audit log")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Customs Admin Dashboard | Manage rules without code deployment</p>
</div>
""", unsafe_allow_html=True)