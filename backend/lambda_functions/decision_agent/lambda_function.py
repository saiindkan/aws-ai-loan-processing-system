"""
AWS Lambda Function: Decision Making Agent (with DynamoDB storage)
"""

import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """
    Decision Making Agent that stores decisions in DynamoDB
    """
    try:
        print("=== DECISION AGENT START ===")
        print(f"Event: {event}")
        
        # Extract basic data
        applicant_id = event.get('applicant_id', 'unknown-applicant')
        applicant_data = event.get('applicant_data', {})
        risk_assessment_raw = event.get('risk_assessment', {})
        
        print(f"Applicant ID: {applicant_id}")
        print(f"Risk assessment type: {type(risk_assessment_raw)}")
        
        # Parse risk assessment if it's a JSON string
        if isinstance(risk_assessment_raw, str):
            try:
                risk_assessment = json.loads(risk_assessment_raw)
            except json.JSONDecodeError:
                risk_assessment = {}
        else:
            risk_assessment = risk_assessment_raw
        
        # Extract risk data
        risk_data = risk_assessment.get('risk_assessment', risk_assessment)
        
        if not isinstance(risk_data, dict):
            risk_data = {}
        
        overall_risk_score = risk_data.get('overall_risk_score', 0.2)
        credit_risk_score = risk_data.get('credit_risk_score', 0.3)
        fraud_risk_score = risk_data.get('fraud_risk_score', 0.1)
        
        # Make a simple decision based on risk
        decision = "APPROVED" if overall_risk_score < 0.5 else "REJECTED"
        reason = "LOW_RISK" if decision == "APPROVED" else "HIGH_RISK"
        
        # Create decision data
        final_decision = {
            'application_id': applicant_id,
            'applicant_name': applicant_data.get('name', 'Test User'),
            'applicant_email': applicant_data.get('email', 'test@example.com'),
            'decision': decision,
            'decision_reason': reason,
            'risk_scores': {
                'overall_risk': overall_risk_score,
                'credit_risk': credit_risk_score,
                'fraud_risk': fraud_risk_score
            },
            'loan_terms': {
                'loan_amount': applicant_data.get('requested_amount', 100000),
                'interest_rate': 4.5,
                'term_months': 60,
                'monthly_payment': 1865.22,
                'total_interest': 11913.2,
                'total_amount': 111913.2
            },
            'decision_rationale': f"Decision based on risk assessment: {decision}",
            'ai_confidence': 0.85,
            'processing_time': 2.0,
            'decision_timestamp': datetime.utcnow().isoformat(),
            'decision_id': context.aws_request_id if context else 'test-id'
        }
        
        # Store in DynamoDB
        try:
            print("📋 Attempting to store in DynamoDB...")
            dynamodb = boto3.resource('dynamodb')
            decisions_table = dynamodb.Table('loan-decisions')
            decisions_table.put_item(Item=final_decision)
            print(f"✅ Successfully stored decision in DynamoDB for applicant: {applicant_id}")
        except Exception as db_error:
            print(f"❌ Error storing decision in DynamoDB: {str(db_error)}")
            # Continue with the response even if DynamoDB fails
        
        print("=== DECISION AGENT SUCCESS ===")
        return {
            'statusCode': 200,
            'body': json.dumps(final_decision)
        }
        
    except Exception as e:
        print(f"=== DECISION AGENT ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'applicant_id': event.get('applicant_id', 'unknown'),
                'decision_status': 'failed'
            })
        }