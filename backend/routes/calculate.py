import sys

from fastapi import APIRouter
sys.path.append('..')

from models import CalculationInput, CalculationResult, ClassificationResult, ChargeBreakdown
from services.classifier import ProductClassifier
from services.calculator import CustomsCalculator

router = APIRouter(prefix="/api", tags=["Calculation"])

# Initialize services
classifier = ProductClassifier()
calculator = CustomsCalculator()

@router.post("/calculate", response_model=CalculationResult)
def calculate_customs(order: CalculationInput):
    """
    Calculate complete customs charges for an order
    
    Steps:
    1. Classify product using AI
    2. Apply customs rules based on classification
    3. Calculate duty, GST, and fees
    4. Return complete breakdown
    """
    start_time = time.time()
    
    # Step 1: Classify
    classification = classifier.classify(order.product_description)
    
    # Step 2: Calculate charges
    total_price = order.price_usd * order.quantity
    total_weight = order.weight_kg * order.quantity
    
    charges = calculator.calculate(
        category=classification['category'],
        origin=order.origin_country,
        destination=order.destination_country,
        price_usd=total_price,
        weight_kg=total_weight
    )
    
    # Step 3: Generate order ID
    order_id = str(uuid.uuid4())[:8].upper()
    
    # Calculate processing time
    processing_time = round(time.time() - start_time, 2)
    
    # Return complete result
    return {
        'order_id': order_id,
        'timestamp': datetime.now().isoformat(),
        'classification': classification,
        'charges': charges,
        'processing_time_seconds': processing_time
    }