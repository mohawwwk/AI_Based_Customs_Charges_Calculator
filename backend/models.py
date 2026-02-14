from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductInput(BaseModel):
    """Input model for product classification"""
    description: str = Field(..., example="Sony WH-1000XM5 Wireless Headphones")
    
class ClassificationResult(BaseModel):
    """Output model for product classification"""
    category: str
    hs_code: str
    confidence: float
    keywords: List[str]
    requires_manual_review: bool

class CalculationInput(BaseModel):
    """Input model for customs calculation"""
    product_description: str = Field(..., example="Sony WH-1000XM5 Wireless Headphones")
    origin_country: str = Field(..., example="USA")
    destination_country: str = Field(..., example="India")
    price_usd: float = Field(..., gt=0, example=399.0)
    weight_kg: float = Field(..., gt=0, example=0.8)
    quantity: int = Field(..., gt=0, example=1)

class ChargeBreakdown(BaseModel):
    """Detailed breakdown of customs charges"""
    exchange_rate: float
    base_price_inr: float
    duty_rate: float
    duty_amount: float
    duty_regulation: str
    assessable_value: float
    gst_rate: float
    gst_amount: float
    customs_handling: float
    port_charges: float
    documentation: float
    total_fees: float
    total_charges_inr: float
    total_charges_usd: float

class CalculationResult(BaseModel):
    """Complete calculation result"""
    order_id: str
    timestamp: str
    classification: ClassificationResult
    charges: ChargeBreakdown
    processing_time_seconds: float

class CustomsRule(BaseModel):
    """Model for customs rule"""
    id: Optional[int] = None
    origin_country: str
    destination_country: str
    product_category: str
    hs_code: str
    base_duty_rate: float
    gst_rate: float
    regulation_reference: str
    notes: Optional[str] = None