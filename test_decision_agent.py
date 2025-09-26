#!/usr/bin/env python3
"""
Test script to debug the decision agent input format
"""

import json

# Simulate the actual input the decision agent receives from Step Functions
test_event = {
    "applicant_id": "test-123",
    "applicant_data": {
        "name": "Jane Smith",
        "email": "jane.smith@email.com",
        "annual_income": 75000,
        "credit_score": 720,
        "requested_amount": 300000
    },
    "risk_assessment": '{"applicant_id": "test-123", "risk_assessment": {"applicant_id": "test-123", "credit_risk_score": 0.3, "credit_risk_level": "MEDIUM", "fraud_risk_score": -0.5, "fraud_risk_level": "HIGH", "market_risk_score": 0.15, "operational_risk_score": 0.1, "overall_risk_score": 0.01}, "credit_risk": {"risk_score": 0.3, "risk_level": "MEDIUM"}}'
}

def test_parsing():
    print("Testing decision agent input parsing...")
    
    # Extract data from event
    applicant_id = test_event.get('applicant_id')
    applicant_data = test_event.get('applicant_data', {})
    risk_assessment_raw = test_event.get('risk_assessment', {})
    
    print(f"1. applicant_id: {applicant_id}")
    print(f"2. applicant_data type: {type(applicant_data)}")
    print(f"3. risk_assessment_raw type: {type(risk_assessment_raw)}")
    print(f"4. risk_assessment_raw: {risk_assessment_raw}")
    
    # Parse risk assessment if it's a JSON string
    if isinstance(risk_assessment_raw, str):
        try:
            risk_assessment = json.loads(risk_assessment_raw)
            print(f"5. Successfully parsed risk_assessment: {type(risk_assessment)}")
        except json.JSONDecodeError as e:
            print(f"5. Failed to parse risk_assessment: {e}")
            risk_assessment = {}
    else:
        risk_assessment = risk_assessment_raw
    
    # Check if risk_assessment is nested under 'risk_assessment' key
    if 'risk_assessment' in risk_assessment:
        risk_data = risk_assessment['risk_assessment']
        print(f"6. Found nested risk_assessment: {type(risk_data)}")
    else:
        risk_data = risk_assessment
        print(f"6. Using top-level risk_assessment: {type(risk_data)}")
    
    # Try to extract risk scores
    try:
        overall_risk_score = risk_data.get('overall_risk_score', 0.5)
        credit_risk_score = risk_data.get('credit_risk_score', 0.5)
        print(f"7. Successfully extracted risk scores: overall={overall_risk_score}, credit={credit_risk_score}")
    except Exception as e:
        print(f"7. Error extracting risk scores: {e}")
        print(f"   risk_data type: {type(risk_data)}")
        print(f"   risk_data: {risk_data}")

if __name__ == '__main__':
    test_parsing()
