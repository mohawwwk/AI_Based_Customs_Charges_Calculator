import sys

from fastapi import APIRouter
sys.path.append('..')

from models import ProductInput, ClassificationResult
from services.classifier import ProductClassifier

router = APIRouter(prefix="/api", tags=["Classification"])

# Initialize classifier
classifier = ProductClassifier()

@router.post("/classify", response_model=ClassificationResult)
def classify_product(product: ProductInput):
    """
    Classify a product based on its description
    
    - **description**: Product description (e.g., "Sony wireless headphones")
    
    Returns classification with category, HS code, and confidence score
    """
    result = classifier.classify(product.description)
    return result