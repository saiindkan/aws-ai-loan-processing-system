"""
AWS Lambda Function: Simple Decision Making Agent (for debugging)
This agent makes final loan decisions based on risk assessments and business rules
"""

import json
import boto3
from typing import Dict, Any
from datetime import datetime

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simple AI Decision Making Agent
    Makes final loan decisions based on comprehensive risk assessment
    """
    try:
        print(f"Making decision for applicant: {event.get('applicant_id')}")
        
        # Extract data from event
        applicant_id = event.get('applicant_id')
        applicant_data = event.get('applicant_data', {})
        risk_assessment_raw = event.get('risk_assessment', {})
        
        print(f"Input types - applicant_id: {type(applicant_id)}, applicant_data: {type(applicant_data)}, risk_assessment: {type(risk_assessment_raw)}")
        
        # Parse risk assessment if it's a JSON string
        if isinstance(risk_assessment_raw, str):
            try:
                risk_assessment = json.loads(risk_assessment_raw)
            except json.JSONDecodeError:
                risk_assessment = {}
        else:
            risk_assessment = risk_assessment_raw
        
        # Extract risk scores from the parsed risk assessment
        if 'risk_assessment' in risk_assessment:
            risk_data = risk_assessment['risk_assessment']
        else:
            risk_data = risk_assessment
        
        # Simple decision logic
        overall_risk_score = risk_data.get('overall_risk_score', 0.5) if isinstance(risk_data, dict) else 0.5
        credit_score = applicant_data.get('credit_score', 650)
        annual_income = applicant_data.get('annual_income', 50000)
        
        # Make simple decision
        if credit_score >= 700 and annual_income >= 50000:
            decision = "APPROVED"
            decision_reason = "GOOD_CREDIT_AND_INCOME"
        elif credit_score < 500:
            decision = "REJECTED"
            decision_reason = "POOR_CREDIT"
        else:
            decision = "CONDITIONAL_APPROVAL"
            decision_reason = "MODERATE_RISK"
        
        # Calculate simple loan terms
        loan_amount = applicant_data.get('requested_amount', 50000)
        interest_rate = 4.5 if decision == "APPROVED" else 6.5
        term_months = 60
        monthly_payment = loan_amount * (interest_rate / 100 / 12) * ((1 + interest_rate / 100 / 12) ** term_months) / (((1 + interest_rate / 100 / 12) ** term_months) - 1)
        
        # Prepare final decision
        final_decision = {
            'application_id': applicant_id,
            'applicant_name': applicant_data.get('name', 'Unknown'),
            'applicant_email': applicant_data.get('email', ''),
            'decision': decision,
            'decision_reason': decision_reason,
            'risk_scores': {
                'overall_risk': overall_risk_score,
                'credit_risk': 0.3,
                'fraud_risk': 0.1
            },
            'loan_terms': {
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'term_months': term_months,
                'monthly_payment': round(monthly_payment, 2),
                'total_interest': round(monthly_payment * term_months - loan_amount, 2),
                'total_amount': round(monthly_payment * term_months, 2)
            } if decision != "REJECTED" else {},
            'decision_rationale': f"Decision: {decision} | Credit Score: {credit_score} | Income: ${annual_income:,.2f}",
            'ai_confidence': 0.85,
            'processing_time': 5.0,
            'decision_timestamp': datetime.utcnow().isoformat(),
            'decision_id': context.aws_request_id
        }
        
        # Store decision in DynamoDB
        try:
            dynamodb = boto3.resource('dynamodb')
            decisions_table = dynamodb.Table('loan-decisions')
            decisions_table.put_item(Item=final_decision)
            print("✅ Successfully stored decision in DynamoDB")
        except Exception as e:
            print(f"Warning: Could not store decision in DynamoDB: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(final_decision)
        }
        
    except Exception as e:
        print(f"Error in decision making: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'applicant_id': applicant_id,
                'decision_status': 'failed'
            })
        }
