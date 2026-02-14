from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from database import db

router = APIRouter(prefix="/admin", tags=["Admin"])

# -------------------- PYDANTIC MODELS --------------------

class CustomsRuleResponse(BaseModel):
    """Response model for customs rule"""
    id: int
    origin_country: str
    destination_country: str
    product_category: str
    hs_code: str
    base_duty_rate: float
    gst_rate: float
    regulation_reference: str
    notes: Optional[str] = None
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None

class CustomsRuleCreate(BaseModel):
    """Model for creating new rule"""
    origin_country: str = Field(..., example="USA")
    destination_country: str = Field(..., example="India")
    product_category: str = Field(..., example="Electronics")
    hs_code: str = Field(..., example="8518.30.00")
    base_duty_rate: float = Field(..., ge=0, le=1, example=0.15)
    gst_rate: float = Field(..., ge=0, le=1, example=0.18)
    regulation_reference: str = Field(..., example="India Customs Tariff Act 2024")
    notes: Optional[str] = Field(None, example="Audio equipment")

class CustomsRuleUpdate(BaseModel):
    """Model for updating existing rule"""
    base_duty_rate: Optional[float] = Field(None, ge=0, le=1)
    gst_rate: Optional[float] = Field(None, ge=0, le=1)
    regulation_reference: Optional[str] = None
    notes: Optional[str] = None

# -------------------- ENDPOINTS --------------------

@router.get("/rules", response_model=List[CustomsRuleResponse])
def get_all_rules():
    """
    Get all customs rules
    
    Returns list of all customs rules in the database
    """
    try:
        rules = db.get_all_rules()
        
        # Convert datetime objects to strings
        for rule in rules:
            if 'effective_from' in rule and rule['effective_from']:
                rule['effective_from'] = str(rule['effective_from'])
            if 'effective_until' in rule and rule['effective_until']:
                rule['effective_until'] = str(rule['effective_until'])
        
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rules: {str(e)}")

@router.get("/rules/{rule_id}", response_model=CustomsRuleResponse)
def get_rule(rule_id: int):
    """
    Get a specific customs rule by ID
    """
    try:
        rule = db.get_rule_by_id(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule with ID {rule_id} not found")
        
        # Convert datetime to string
        if 'effective_from' in rule and rule['effective_from']:
            rule['effective_from'] = str(rule['effective_from'])
        if 'effective_until' in rule and rule['effective_until']:
            rule['effective_until'] = str(rule['effective_until'])
        
        return rule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rule: {str(e)}")

@router.post("/rules", status_code=201)
def create_rule(rule: CustomsRuleCreate):
    """
    Create a new customs rule
    
    Requires all fields:
    - origin_country, destination_country, product_category
    - hs_code, base_duty_rate, gst_rate
    - regulation_reference
    """
    try:
        success = db.add_rule(
            origin=rule.origin_country,
            destination=rule.destination_country,
            category=rule.product_category,
            hs_code=rule.hs_code,
            duty_rate=rule.base_duty_rate,
            gst_rate=rule.gst_rate,
            regulation=rule.regulation_reference,
            notes=rule.notes or ""
        )
        
        if success:
            return {
                "success": True,
                "message": "Customs rule created successfully",
                "rule": rule.dict()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create rule")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating rule: {str(e)}")

@router.put("/rules/{rule_id}")
def update_rule(rule_id: int, updates: CustomsRuleUpdate):
    """
    Update an existing customs rule
    
    Only provide fields you want to update.
    All fields are optional.
    """
    try:
        # Get existing rule
        existing_rule = db.get_rule_by_id(rule_id)
        
        if not existing_rule:
            raise HTTPException(status_code=404, detail=f"Rule with ID {rule_id} not found")
        
        # Use existing values if not provided in update
        duty_rate = updates.base_duty_rate if updates.base_duty_rate is not None else float(existing_rule['base_duty_rate'])
        gst_rate = updates.gst_rate if updates.gst_rate is not None else float(existing_rule['gst_rate'])
        regulation = updates.regulation_reference if updates.regulation_reference else existing_rule['regulation_reference']
        notes = updates.notes if updates.notes else existing_rule.get('notes', '')
        
        success = db.update_rule(
            rule_id=rule_id,
            duty_rate=duty_rate,
            gst_rate=gst_rate,
            regulation=regulation,
            notes=notes
        )
        
        if success:
            return {
                "success": True,
                "message": f"Rule {rule_id} updated successfully",
                "updated_fields": updates.dict(exclude_none=True)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update rule")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int):
    """
    Delete a customs rule
    
    ⚠️ WARNING: This permanently deletes the rule!
    """
    try:
        # Check if rule exists
        existing_rule = db.get_rule_by_id(rule_id)
        
        if not existing_rule:
            raise HTTPException(status_code=404, detail=f"Rule with ID {rule_id} not found")
        
        success = db.delete_rule(rule_id)
        
        if success:
            return {
                "success": True,
                "message": f"Rule {rule_id} deleted successfully",
                "deleted_rule": {
                    "id": rule_id,
                    "category": existing_rule['product_category'],
                    "route": f"{existing_rule['origin_country']} → {existing_rule['destination_country']}"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete rule")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting rule: {str(e)}")

@router.get("/audit-log")
def get_audit_log(limit: int = 50):
    """
    Get recent calculation audit logs
    
    Parameters:
    - limit: Number of records to return (default: 50, max: 500)
    """
    try:
        if limit > 500:
            limit = 500
        
        logs = db.get_audit_log(limit=limit)
        
        # Convert datetime to string
        for log in logs:
            if 'timestamp' in log and log['timestamp']:
                log['timestamp'] = str(log['timestamp'])
        
        return {
            "success": True,
            "count": len(logs),
            "logs": logs
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching audit log: {str(e)}")

@router.get("/stats")
def get_statistics():
    """
    Get system statistics
    
    Returns:
    - Total rules
    - Total calculations
    - Rules by country
    - Recent activity
    """
    try:
        stats = db.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")