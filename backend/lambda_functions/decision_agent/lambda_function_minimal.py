"""
AWS Lambda Function: Minimal Decision Making Agent (for debugging)
"""

import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Minimal Decision Making Agent for debugging
    """
    try:
        print("=== DECISION AGENT DEBUG START ===")
        print(f"Event type: {type(event)}")
        print(f"Event: {event}")
        
        # Extract basic data
        applicant_id = event.get('applicant_id') if hasattr(event, 'get') else event['applicant_id'] if 'applicant_id' in event else 'unknown'
        
        print(f"Applicant ID: {applicant_id}")
        
        # Create minimal decision
        final_decision = {
            'application_id': applicant_id,
            'applicant_name': 'Test User',
            'applicant_email': 'test@example.com',
            'decision': 'APPROVED',
            'decision_reason': 'TEST_APPROVAL',
            'risk_scores': {
                'overall_risk': 0.2,
                'credit_risk': 0.3,
                'fraud_risk': 0.1
            },
            'loan_terms': {
                'loan_amount': 100000,
                'interest_rate': 4.5,
                'term_months': 60,
                'monthly_payment': 1865.22,
                'total_interest': 11913.20,
                'total_amount': 111913.20
            },
            'decision_rationale': 'Test decision for debugging',
            'ai_confidence': 0.85,
            'processing_time': 2.0,
            'decision_timestamp': datetime.utcnow().isoformat(),
            'decision_id': context.aws_request_id if context else 'test-id'
        }
        
        print("=== DECISION AGENT DEBUG SUCCESS ===")
        return {
            'statusCode': 200,
            'body': json.dumps(final_decision)
        }
        
    except Exception as e:
        print(f"=== DECISION AGENT DEBUG ERROR ===")
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'applicant_id': 'unknown',
                'decision_status': 'failed'
            })
        }
