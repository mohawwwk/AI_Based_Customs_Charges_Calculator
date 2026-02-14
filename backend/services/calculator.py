from typing import Dict
from database import db

class CustomsCalculator:
    """
    Rule-based customs calculation engine
    NOW USES MYSQL DATABASE!
    """
    
    def __init__(self):
        self.exchange_rate = 83.0
    
    def calculate(self, category: str, origin: str, destination: str,
                  price_usd: float, weight_kg: float) -> Dict:
        """
        Calculate customs charges using database rules
        """
        
        # Get rule from DATABASE (not hardcoded!)
        rule = db.get_customs_rule(origin, destination, category)
        
        if not rule:
            # Default if no rule found
            rule = {
                'base_duty_rate': 0.10,
                'gst_rate': 0.18,
                'regulation_reference': 'Default rate - No specific rule found'
            }
        
        # Convert to INR
        base_price_inr = price_usd * self.exchange_rate
        
        # Calculate duty
        duty_rate = float(rule['base_duty_rate'])
        duty_amount = base_price_inr * duty_rate
        
        # Calculate assessable value
        assessable_value = base_price_inr + duty_amount
        
        # Calculate GST
        gst_rate = float(rule['gst_rate'])
        gst_amount = assessable_value * gst_rate
        
        # Get fees from DATABASE
        fees = db.get_fees(destination)
        
        customs_handling = 0
        port_charges = 0
        documentation = 0
        
        for fee in fees:
            if fee['fee_name'] == 'Customs Handling Fee':
                customs_handling = float(fee['amount'])
            elif fee['fee_name'] == 'Port Handling Charges':
                port_charges = float(fee['amount']) * weight_kg
            elif fee['fee_name'] == 'Documentation Fee':
                documentation = float(fee['amount'])
        
        total_fees = customs_handling + port_charges + documentation
        
        # Calculate totals
        total_charges_inr = duty_amount + gst_amount + total_fees
        total_charges_usd = total_charges_inr / self.exchange_rate
        
        return {
            'exchange_rate': self.exchange_rate,
            'base_price_inr': round(base_price_inr, 2),
            'duty_rate': duty_rate,
            'duty_amount': round(duty_amount, 2),
            'duty_regulation': rule['regulation_reference'],
            'assessable_value': round(assessable_value, 2),
            'gst_rate': gst_rate,
            'gst_amount': round(gst_amount, 2),
            'customs_handling': customs_handling,
            'port_charges': round(port_charges, 2),
            'documentation': documentation,
            'total_fees': round(total_fees, 2),
            'total_charges_inr': round(total_charges_inr, 2),
            'total_charges_usd': round(total_charges_usd, 2)
        }