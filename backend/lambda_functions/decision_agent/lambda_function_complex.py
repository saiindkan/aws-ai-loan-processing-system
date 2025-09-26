"""
AWS Lambda Function: Decision Making Agent
This agent makes final loan decisions based on risk assessments and business rules
"""

import json
import boto3
from typing import Dict, Any
from datetime import datetime, timedelta

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AI Decision Making Agent
    Makes final loan decisions based on comprehensive risk assessment
    """
    try:
        print(f"Making decision for applicant: {event.get('applicant_id')}")
        
        # Extract data from event
        applicant_id = event.get('applicant_id')
        applicant_data = event.get('applicant_data', {})
        risk_assessment_raw = event.get('risk_assessment', {})
        
        # Parse risk assessment if it's a JSON string
        if isinstance(risk_assessment_raw, str):
            try:
                risk_assessment = json.loads(risk_assessment_raw)
            except json.JSONDecodeError:
                risk_assessment = {}
        else:
            risk_assessment = risk_assessment_raw
        
        # Additional check: if risk_assessment is still a string, try to parse it again
        if isinstance(risk_assessment, str):
            try:
                risk_assessment = json.loads(risk_assessment)
            except json.JSONDecodeError:
                risk_assessment = {}
        
        # Debug: Print the structure of risk_assessment
        print(f"Risk assessment type: {type(risk_assessment)}")
        print(f"Risk assessment keys: {list(risk_assessment.keys()) if isinstance(risk_assessment, dict) else 'Not a dict'}")
        print(f"Risk assessment: {risk_assessment}")
        
        # Additional debugging for the raw input
        print(f"Risk assessment raw type: {type(risk_assessment_raw)}")
        print(f"Risk assessment raw: {risk_assessment_raw}")
        
        # Debug the full event structure
        print(f"Full event keys: {list(event.keys())}")
        print(f"Event structure: {event}")
        
        # Check if risk_assessment is still a string after parsing
        if isinstance(risk_assessment, str):
            print(f"WARNING: risk_assessment is still a string after parsing: {risk_assessment}")
            try:
                risk_assessment = json.loads(risk_assessment)
                print(f"Successfully parsed risk_assessment: {risk_assessment}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse risk_assessment as JSON: {e}")
                risk_assessment = {}
        
        if not applicant_data or not risk_assessment or not applicant_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required data for decision making',
                    'applicant_id': applicant_id
                })
            }
        
        # Initialize AWS services
        dynamodb = boto3.resource('dynamodb')
        sns_client = boto3.client('sns')
        
        # Extract risk scores from the parsed risk assessment
        # The risk_assessment might be nested under 'risk_assessment' key
        if 'risk_assessment' in risk_assessment:
            risk_data = risk_assessment['risk_assessment']
        else:
            risk_data = risk_assessment
        
        # Additional check: if risk_data is still a string, try to parse it
        if isinstance(risk_data, str):
            try:
                risk_data = json.loads(risk_data)
            except json.JSONDecodeError:
                risk_data = {}
        
        # Ensure risk_data is a dictionary
        if not isinstance(risk_data, dict):
            print(f"Error: risk_data is not a dict, it's {type(risk_data)}: {risk_data}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': f'Invalid risk_data type: {type(risk_data)}',
                    'applicant_id': applicant_id,
                    'decision_status': 'failed'
                })
            }
        
        # Extract risk scores with proper error handling
        try:
            overall_risk_score = risk_data.get('overall_risk_score', 0.5)
            credit_risk_score = risk_data.get('credit_risk_score', 0.5)
            fraud_risk_score = risk_data.get('fraud_risk_score', 0.0)
            fraud_risk_level = risk_data.get('fraud_risk_level', 'LOW')
        except Exception as e:
            print(f"Error extracting risk scores: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': f'Error extracting risk scores: {str(e)}',
                    'applicant_id': applicant_id,
                    'decision_status': 'failed'
                })
            }
        
        # Make decision based on risk scores and business rules
        decision_result = make_loan_decision(
            applicant_data,
            overall_risk_score,
            credit_risk_score,
            fraud_risk_score,
            fraud_risk_level
        )
        
        # Calculate loan terms if approved
        loan_terms = {}
        if decision_result['decision'] == 'APPROVED':
            loan_terms = calculate_loan_terms(
                applicant_data,
                overall_risk_score,
                credit_risk_score
            )
        
        # Generate decision rationale
        print(f"About to call generate_decision_rationale with risk_data type: {type(risk_data)}")
        print(f"risk_data content: {risk_data}")
        decision_rationale = generate_decision_rationale(
            applicant_data,
            risk_data,
            decision_result,
            loan_terms
        )
        
        # Calculate AI confidence
        ai_confidence = calculate_ai_confidence(
            risk_data,
            decision_result,
            applicant_data
        )
        
        # Prepare final decision
        final_decision = {
            'application_id': applicant_id,
            'applicant_name': applicant_data.get('name', 'Unknown'),
            'applicant_email': applicant_data.get('email', ''),
            'decision': decision_result['decision'],
            'decision_reason': decision_result['reason'],
            'risk_scores': {
                'overall_risk': overall_risk_score,
                'credit_risk': credit_risk_score,
                'fraud_risk': fraud_risk_score
            },
            'loan_terms': loan_terms,
            'decision_rationale': decision_rationale,
            'ai_confidence': ai_confidence,
            'processing_time': calculate_processing_time(event),
            'decision_timestamp': datetime.utcnow().isoformat(),
            'decision_id': context.aws_request_id
        }
        
        # Store decision in DynamoDB
        try:
            decisions_table = dynamodb.Table('loan-decisions')
            decisions_table.put_item(Item=final_decision)
        except Exception as e:
            print(f"Warning: Could not store decision in DynamoDB: {str(e)}")
        
        # Send notification
        try:
            send_decision_notification(final_decision, sns_client)
        except Exception as e:
            print(f"Warning: Could not send notification: {str(e)}")
        
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

def make_loan_decision(
    applicant_data: Dict,
    overall_risk_score: float,
    credit_risk_score: float,
    fraud_risk_score: float,
    fraud_risk_level: str
) -> Dict:
    """Make loan decision based on risk scores and business rules"""
    
    # Hard rejection rules
    if fraud_risk_level == 'HIGH' or fraud_risk_score < -0.5:
        return {
            'decision': 'REJECTED',
            'reason': 'HIGH_FRAUD_RISK',
            'confidence': 0.95
        }
    
    if applicant_data.get('credit_score', 0) < 300:
        return {
            'decision': 'REJECTED',
            'reason': 'INSUFFICIENT_CREDIT_SCORE',
            'confidence': 0.90
        }
    
    if applicant_data.get('annual_income', 0) < 15000:
        return {
            'decision': 'REJECTED',
            'reason': 'INSUFFICIENT_INCOME',
            'confidence': 0.85
        }
    
    # Risk-based decision
    if overall_risk_score < 0.2:
        return {
            'decision': 'APPROVED',
            'reason': 'LOW_RISK',
            'confidence': 0.90
        }
    elif overall_risk_score < 0.4:
        return {
            'decision': 'APPROVED',
            'reason': 'MEDIUM_RISK',
            'confidence': 0.75
        }
    elif overall_risk_score < 0.6:
        return {
            'decision': 'CONDITIONAL_APPROVAL',
            'reason': 'HIGH_RISK',
            'confidence': 0.65
        }
    else:
        return {
            'decision': 'REJECTED',
            'reason': 'EXCESSIVE_RISK',
            'confidence': 0.80
        }

def calculate_loan_terms(
    applicant_data: Dict,
    overall_risk_score: float,
    credit_risk_score: float
) -> Dict:
    """Calculate loan terms based on risk assessment"""
    
    loan_amount = applicant_data.get('requested_amount', 50000)
    annual_income = applicant_data.get('annual_income', 50000)
    
    # Base interest rate
    base_rate = 3.5
    
    # Adjust interest rate based on risk
    if overall_risk_score < 0.2:
        interest_rate = base_rate
        term_months = 60
    elif overall_risk_score < 0.4:
        interest_rate = base_rate + 0.5
        term_months = 48
    elif overall_risk_score < 0.6:
        interest_rate = base_rate + 1.0
        term_months = 36
    else:
        interest_rate = base_rate + 2.0
        term_months = 24
    
    # Calculate monthly payment
    monthly_rate = interest_rate / 100 / 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
    
    # Calculate debt-to-income ratio
    debt_to_income = monthly_payment * 12 / annual_income
    
    # Adjust terms if debt-to-income is too high
    if debt_to_income > 0.4:
        # Extend term to reduce monthly payment
        term_months = min(term_months + 12, 72)
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
    
    return {
        'loan_amount': loan_amount,
        'interest_rate': round(interest_rate, 2),
        'term_months': term_months,
        'monthly_payment': round(monthly_payment, 2),
        'total_interest': round(monthly_payment * term_months - loan_amount, 2),
        'total_amount': round(monthly_payment * term_months, 2),
        'debt_to_income_ratio': round(debt_to_income, 3),
        'apr': round(interest_rate, 2)
    }

def generate_decision_rationale(
    applicant_data: Dict,
    risk_assessment: Dict,
    decision_result: Dict,
    loan_terms: Dict
) -> str:
    """Generate human-readable decision rationale"""
    
    rationale_parts = []
    
    # Decision summary
    decision = decision_result['decision']
    reason = decision_result['reason']
    
    rationale_parts.append(f"Decision: {decision}")
    rationale_parts.append(f"Reason: {reason}")
    
    # Risk factors
    overall_risk = risk_assessment.get('overall_risk_score', 0.5)
    credit_risk = risk_assessment.get('credit_risk_score', 0.5)
    fraud_risk = risk_assessment.get('fraud_risk_score', 0.0)
    
    rationale_parts.append(f"Overall Risk Score: {overall_risk:.2f}")
    rationale_parts.append(f"Credit Risk Score: {credit_risk:.2f}")
    rationale_parts.append(f"Fraud Risk Score: {fraud_risk:.2f}")
    
    # Key factors
    credit_score = applicant_data.get('credit_score', 0)
    annual_income = applicant_data.get('annual_income', 0)
    employment_years = applicant_data.get('employment_years', 2)
    
    rationale_parts.append(f"Credit Score: {credit_score}")
    rationale_parts.append(f"Annual Income: ${annual_income:,.2f}")
    rationale_parts.append(f"Employment Years: {employment_years}")
    
    # Loan terms (if approved)
    if decision == 'APPROVED' and loan_terms:
        rationale_parts.append(f"Approved Amount: ${loan_terms['loan_amount']:,.2f}")
        rationale_parts.append(f"Interest Rate: {loan_terms['interest_rate']}%")
        rationale_parts.append(f"Term: {loan_terms['term_months']} months")
        rationale_parts.append(f"Monthly Payment: ${loan_terms['monthly_payment']:,.2f}")
    
    return " | ".join(rationale_parts)

def calculate_ai_confidence(
    risk_assessment: Dict,
    decision_result: Dict,
    applicant_data: Dict
) -> float:
    """Calculate AI confidence in the decision"""
    
    base_confidence = 0.7
    
    # Increase confidence for extreme risk scores
    overall_risk = risk_assessment.get('overall_risk_score', 0.5)
    if overall_risk < 0.2 or overall_risk > 0.8:
        base_confidence += 0.1
    
    # Increase confidence for clear credit scores
    credit_score = applicant_data.get('credit_score', 0)
    if credit_score > 750 or credit_score < 500:
        base_confidence += 0.1
    
    # Increase confidence for consistent data
    if applicant_data.get('employment_years', 2) > 5:
        base_confidence += 0.05
    
    # Decrease confidence for missing data
    required_fields = ['credit_score', 'annual_income', 'employment_years']
    missing_fields = [field for field in required_fields if not applicant_data.get(field)]
    base_confidence -= len(missing_fields) * 0.05
    
    return min(max(base_confidence, 0.0), 1.0)

def calculate_processing_time(event: Dict) -> float:
    """Calculate processing time in seconds"""
    start_time = event.get('start_time')
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            processing_time = (datetime.utcnow() - start_dt).total_seconds()
            return round(processing_time, 2)
        except:
            pass
    
    # Default processing time
    return 5.0

def send_decision_notification(decision: Dict, sns_client) -> None:
    """Send decision notification via SNS"""
    try:
        topic_arn = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:loan-decision-notifications'
        
        message = {
            'application_id': decision['application_id'],
            'applicant_name': decision['applicant_name'],
            'decision': decision['decision'],
            'decision_reason': decision['decision_reason'],
            'timestamp': decision['decision_timestamp']
        }
        
        if decision['decision'] == 'APPROVED' and decision.get('loan_terms'):
            message['loan_terms'] = decision['loan_terms']
        
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=f"Loan Decision: {decision['decision']} - {decision['applicant_name']}"
        )
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        raise e
