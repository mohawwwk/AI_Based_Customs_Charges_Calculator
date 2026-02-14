import mysql.connector
from mysql.connector import Error
import json
from typing import Optional, Dict, List
import time

class Database:
    """MySQL Database connection with auto-reconnect"""
    
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "Mohak@069"
        self.database = "customs_calculator"
        self.connection = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def connect(self):
        """Create database connection with retries"""
        for attempt in range(self.max_retries):
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=True
                )
                if self.connection.is_connected():
                    print(f"✅ Connected to MySQL database: {self.database}")
                    return True
            except Error as e:
                print(f"❌ MySQL Connection Error (Attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"   Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("   ❌ Failed to connect to MySQL!")
                    print("   💡 Make sure MySQL is running: net start MySQL80")
                    return False
        return False
    
    def ensure_connection(self):
        """Ensure database is connected, reconnect if needed"""
        if not self.connection or not self.connection.is_connected():
            print("🔄 Reconnecting to database...")
            return self.connect()
        return True
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Disconnected from MySQL")
    
    def get_customs_rule(self, origin: str, destination: str, category: str) -> Optional[Dict]:
        """Get customs rule from database"""
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM customs_rules
                WHERE origin_country = %s
                  AND destination_country = %s
                  AND product_category = %s
                  AND effective_from <= CURDATE()
                  AND (effective_until IS NULL OR effective_until >= CURDATE())
                LIMIT 1
            """
            
            cursor.execute(query, (origin, destination, category))
            result = cursor.fetchone()
            cursor.close()
            
            return result
            
        except Error as e:
            print(f"❌ Error fetching customs rule: {e}")
            return None
    
    def get_fees(self, country: str) -> List[Dict]:
        """Get all fees for a country"""
        if not self.ensure_connection():
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM additional_fees
                WHERE country = %s
            """
            
            cursor.execute(query, (country,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"❌ Error fetching fees: {e}")
            return []
    
    def log_calculation(self, order_id: str, product_desc: str, origin: str, 
                       dest: str, category: str, hs_code: str, confidence: float,
                       price_usd: float, total_inr: float, details: Dict):
        """Log calculation to audit trail"""
        if not self.ensure_connection():
            print("⚠️ Could not log calculation - database not connected")
            return
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO calculation_audit
                (order_id, product_description, origin_country, destination_country,
                 classified_category, hs_code, classification_confidence,
                 base_price_usd, total_charges_inr, calculation_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                order_id, product_desc, origin, dest, category, hs_code,
                confidence, price_usd, total_inr, json.dumps(details)
            ))
            
            cursor.close()
            print(f"✅ Logged calculation: Order {order_id}")
            
        except Error as e:
            print(f"❌ Error logging calculation: {e}")
    
    def get_all_rules(self) -> List[Dict]:
        """Get all customs rules"""
        if not self.ensure_connection():
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM customs_rules
                ORDER BY origin_country, destination_country, product_category
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"❌ Error fetching all rules: {e}")
            return []
    
    def get_rule_by_id(self, rule_id: int) -> Optional[Dict]:
        """Get a specific rule by ID"""
        if not self.ensure_connection():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM customs_rules WHERE id = %s"
            cursor.execute(query, (rule_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result
            
        except Error as e:
            print(f"❌ Error fetching rule by ID: {e}")
            return None
    
    def update_rule(self, rule_id: int, duty_rate: float, gst_rate: float, 
                   regulation: str, notes: str):
        """Update an existing rule"""
        if not self.ensure_connection():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                UPDATE customs_rules
                SET base_duty_rate = %s,
                    gst_rate = %s,
                    regulation_reference = %s,
                    notes = %s
                WHERE id = %s
            """
            
            cursor.execute(query, (duty_rate, gst_rate, regulation, notes, rule_id))
            cursor.close()
            
            print(f"✅ Updated rule ID {rule_id}")
            return True
            
        except Error as e:
            print(f"❌ Error updating rule: {e}")
            return False
    
    def add_rule(self, origin: str, destination: str, category: str, hs_code: str,
                duty_rate: float, gst_rate: float, regulation: str, notes: str):
        """Add new customs rule"""
        if not self.ensure_connection():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO customs_rules
                (origin_country, destination_country, product_category, hs_code,
                 base_duty_rate, gst_rate, regulation_reference, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (origin, destination, category, hs_code,
                                 duty_rate, gst_rate, regulation, notes))
            cursor.close()
            
            print(f"✅ Added new rule: {category} ({origin} → {destination})")
            return True
            
        except Error as e:
            print(f"❌ Error adding rule: {e}")
            return False
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a customs rule"""
        if not self.ensure_connection():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            query = "DELETE FROM customs_rules WHERE id = %s"
            cursor.execute(query, (rule_id,))
            cursor.close()
            
            print(f"✅ Deleted rule ID {rule_id}")
            return True
            
        except Error as e:
            print(f"❌ Error deleting rule: {e}")
            return False
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get audit log entries"""
        if not self.ensure_connection():
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM calculation_audit
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"❌ Error fetching audit log: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        if not self.ensure_connection():
            return {}
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            stats = {}
            
            # Total rules
            cursor.execute("SELECT COUNT(*) as count FROM customs_rules")
            stats['total_rules'] = cursor.fetchone()['count']
            
            # Total calculations
            cursor.execute("SELECT COUNT(*) as count FROM calculation_audit")
            stats['total_calculations'] = cursor.fetchone()['count']
            
            # Rules by country
            cursor.execute("""
                SELECT origin_country, destination_country, COUNT(*) as count
                FROM customs_rules
                GROUP BY origin_country, destination_country
            """)
            stats['rules_by_route'] = cursor.fetchall()
            
            # Recent calculations by category
            cursor.execute("""
                SELECT classified_category, COUNT(*) as count
                FROM calculation_audit
                GROUP BY classified_category
                ORDER BY count DESC
            """)
            stats['calculations_by_category'] = cursor.fetchall()
            
            # Average charges
            cursor.execute("""
                SELECT AVG(total_charges_inr) as avg_charges_inr
                FROM calculation_audit
            """)
            result = cursor.fetchone()
            stats['average_charges_inr'] = float(result['avg_charges_inr']) if result['avg_charges_inr'] else 0
            
            cursor.close()
            
            return stats
            
        except Error as e:
            print(f"❌ Error fetching statistics: {e}")
            return {}

# Create global database instance and connect
print("🔄 Initializing database connection...")
db = Database()
db.connect()