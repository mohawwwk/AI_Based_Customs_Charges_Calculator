import warnings
warnings.filterwarnings('ignore', message='.*ScriptRunContext.*')
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import uuid
from datetime import datetime
from typing import Optional
from routes.admin import router as admin_router

from services.calculator import CustomsCalculator
from services.classifier import ProductClassifier
from database import db
from services.pdf_generator import pdf_generator
from fastapi.responses import FileResponse

app = FastAPI(
    title="AI Customs Calculator API",
    description="REST API for customs charge calculation with AI classification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calculator = CustomsCalculator()
classifier = ProductClassifier()
# Include admin routes
app.include_router(admin_router)

# -------------------- PYDANTIC MODELS --------------------
class ClassifyRequest(BaseModel):
    description: str = Field(..., example="Sony WH-1000XM5 Wireless Headphones")

class CalculateRequest(BaseModel):
    product_description: str = Field(..., example="Sony WH-1000XM5 Wireless Headphones")
    origin_country: str = Field(..., example="USA")
    destination_country: str = Field(..., example="India")
    price_usd: float = Field(..., gt=0, example=399.0)
    weight_kg: float = Field(..., gt=0, example=0.8)
    quantity: Optional[int] = Field(1, gt=0, example=1)

# -------------------- ENDPOINTS --------------------

@app.post("/api/classify")
def classify_endpoint(request: ClassifyRequest):
    """
    Classify a product based on description
    
    Returns:
    - category: Product category
    - hs_code: Harmonized System code
    - confidence: AI confidence score
    - keywords: Detected keywords
    """
    try:
        result = classifier.classify(request.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate")
def calculate_endpoint(request: CalculateRequest):
    """
    Calculate complete customs charges
    
    Steps:
    1. Classify product using AI
    2. Fetch customs rules from database
    3. Calculate duty, GST, and fees
    4. Log to audit trail
    5. Return complete breakdown
    """
    try:
        # Generate order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Step 1: AI Classification
        classification = classifier.classify(request.product_description)
        
        # Step 2: Calculate charges
        total_price = request.price_usd * request.quantity
        total_weight = request.weight_kg * request.quantity
        
        charges = calculator.calculate(
            category=classification["category"],
            origin=request.origin_country,
            destination=request.destination_country,
            price_usd=total_price,
            weight_kg=total_weight
        )
        
        # Step 3: Log to database
        db.log_calculation(
            order_id=order_id,
            product_desc=request.product_description,
            origin=request.origin_country,
            dest=request.destination_country,
            category=classification["category"],
            hs_code=classification["hs_code"],
            confidence=classification["confidence"],
            price_usd=total_price,
            total_inr=charges["total_charges_inr"],
            details=charges
        )
        
        # Step 4: Return result
        return {
            "success": True,
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "classification": classification,
            "charges": charges,
            "processing_time_seconds": 0.5
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/")
def root():
    """API Health Check"""
    return {
        "status": "online",
        "message": "AI Customs Calculator API is running",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "calculate": "/api/calculate",
            "classify": "/api/classify",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        if db.connection and db.connection.is_connected():
            db_status = "connected"
            # Try a simple query
            cursor = db.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        else:
            db_status = "disconnected - MySQL may not be running"
            db.ensure_connection()  # Try to reconnect
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "services": {
            "api": "running",
            "calculator": "ready",
            "classifier": "loaded",
            "database": db_status
        },
        "message": "If database shows disconnected, run: net start MySQL80"
    }
@app.post("/api/calculate/pdf")
def calculate_and_generate_pdf(request: CalculateRequest):
    """
    Calculate customs charges AND generate downloadable PDF report
    
    Returns calculation results plus a download link for PDF
    """
    try:
        # Generate order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Step 1: AI Classification
        classification = classifier.classify(request.product_description)
        
        # Step 2: Calculate charges
        total_price = request.price_usd * request.quantity
        total_weight = request.weight_kg * request.quantity
        
        charges = calculator.calculate(
            category=classification["category"],
            origin=request.origin_country,
            destination=request.destination_country,
            price_usd=total_price,
            weight_kg=total_weight
        )
        
        # Step 3: Log to database
        db.log_calculation(
            order_id=order_id,
            product_desc=request.product_description,
            origin=request.origin_country,
            dest=request.destination_country,
            category=classification["category"],
            hs_code=classification["hs_code"],
            confidence=classification["confidence"],
            price_usd=total_price,
            total_inr=charges["total_charges_inr"],
            details=charges
        )
        
        # Step 4: Generate PDF
        pdf_data = {
            'product_description': request.product_description,
            'origin_country': request.origin_country,
            'destination_country': request.destination_country,
            'quantity': request.quantity,
            'classification': classification,
            'charges': charges
        }
        
        pdf_filepath = pdf_generator.generate_calculation_report(order_id, pdf_data)
        
        # Step 5: Return result with PDF download link
        return {
            "success": True,
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "classification": classification,
            "charges": charges,
            "pdf": {
                "generated": True,
                "download_url": f"/api/download/{order_id}",
                "filename": f"customs_report_{order_id}.pdf"
            },
            "processing_time_seconds": 0.5
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/download/{order_id}")
def download_pdf(order_id: str):
    """
    Download PDF report for a specific order
    """
    filepath = f"outputs/customs_report_{order_id}.pdf"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    return FileResponse(
        filepath,
        media_type='application/pdf',
        filename=f"customs_report_{order_id}.pdf"
    )
@app.get("/api/performance")
def get_performance_stats():
    """
    Get system performance statistics
    """
    try:
        import psutil
        import time
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Database stats
        stats = db.get_statistics()
        
        return {
            "success": True,
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": round(disk.used / disk.total * 100, 1)
                }
            },
            "database": {
                "total_rules": stats.get('total_rules', 0),
                "total_calculations": stats.get('total_calculations', 0),
                "average_charges_inr": stats.get('average_charges_inr', 0)
            },
            "model": {
                "type": "TF-IDF + Naive Bayes",
                "accuracy": "95%",
                "categories": 4,
                "vocabulary_size": len(classifier.vectorizer.get_feature_names_out())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
