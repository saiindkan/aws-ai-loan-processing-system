"""
AWS Lambda Function: Risk Assessment Agent
This agent calculates credit risk, fraud risk, and market risk using ML models
"""

import json
import boto3
from typing import Dict, Any
from datetime import datetime

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AI Risk Assessment Agent
    Calculates comprehensive risk scores using SageMaker models and business logic
    """
    try:
        print(f"Assessing risk for applicant: {event.get('applicant_id')}")
        
        # Extract data from event
        applicant_id = event.get('applicant_id')
        applicant_data = event.get('applicant_data', {})
        extracted_data = event.get('extracted_data', {})
        
        if not applicant_data or not applicant_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No applicant data or ID provided',
                    'applicant_id': applicant_id
                })
            }
        
        # Initialize AWS services
        sagemaker_runtime = boto3.client('sagemaker-runtime')
        dynamodb = boto3.resource('dynamodb')
        
        # Calculate credit risk using SageMaker
        credit_risk_result = calculate_credit_risk(applicant_data, sagemaker_runtime)
        
        # Calculate fraud risk
        fraud_risk_result = calculate_fraud_risk(applicant_data, extracted_data, sagemaker_runtime)
        
        # Calculate market risk
        market_risk_result = calculate_market_risk(applicant_data)
        
        # Calculate operational risk
        operational_risk_result = calculate_operational_risk(applicant_data, extracted_data)
        
        # Calculate overall risk score
        overall_risk_score = calculate_overall_risk(
            credit_risk_result['risk_score'],
            fraud_risk_result['fraud_score'],
            market_risk_result['market_risk_score'],
            operational_risk_result['operational_risk_score']
        )
        
        # Store risk assessment in DynamoDB
        risk_assessment = {
            'applicant_id': applicant_id,
            'credit_risk_score': credit_risk_result['risk_score'],
            'credit_risk_level': credit_risk_result['risk_level'],
            'fraud_risk_score': fraud_risk_result['fraud_score'],
            'fraud_risk_level': fraud_risk_result['fraud_level'],
            'market_risk_score': market_risk_result['market_risk_score'],
            'operational_risk_score': operational_risk_result['operational_risk_score'],
            'overall_risk_score': overall_risk_score,
            'risk_assessment_timestamp': datetime.utcnow().isoformat(),
            'assessment_id': context.aws_request_id
        }
        
        # Store in DynamoDB
        try:
            risk_table = dynamodb.Table('risk-assessments')
            risk_table.put_item(Item=risk_assessment)
        except Exception as e:
            print(f"Warning: Could not store risk assessment in DynamoDB: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'applicant_id': applicant_id,
                'risk_assessment': risk_assessment,
                'credit_risk': credit_risk_result,
                'fraud_risk': fraud_risk_result,
                'market_risk': market_risk_result,
                'operational_risk': operational_risk_result,
                'overall_risk_score': overall_risk_score,
                'assessment_timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error in risk assessment: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'applicant_id': applicant_id,
                'assessment_status': 'failed'
            })
        }

def calculate_credit_risk(applicant_data: Dict, sagemaker_runtime) -> Dict:
    """Calculate credit risk using SageMaker model"""
    try:
        # Prepare features for credit risk model
        credit_score = applicant_data.get('credit_score', 650)
        annual_income = applicant_data.get('annual_income', 50000)
        loan_amount = applicant_data.get('requested_amount', 50000)
        employment_years = applicant_data.get('employment_years', 2)
        
        features = {
            'credit_score_normalized': (credit_score - 300) / 550,
            'annual_income': annual_income,
            'debt_to_income_ratio': applicant_data.get('debt_to_income_ratio', 0.3),
            'employment_years': employment_years,
            'loan_amount': loan_amount,
            'age': applicant_data.get('age', 35),
            'loan_purpose_score': get_loan_purpose_score(applicant_data.get('loan_purpose', 'personal')),
            'previous_defaults': applicant_data.get('previous_defaults', 0),
            'loan_to_income_ratio': loan_amount / annual_income if annual_income > 0 else 1.0
        }
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='credit-risk-model-endpoint',
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        result = json.loads(response['Body'].read())
        risk_score = result['risk_score']
        
        return {
            'risk_score': risk_score,
            'risk_level': get_risk_level(risk_score),
            'confidence': result.get('confidence', 0.85),
            'model_version': 'v1.0'
        }
        
    except Exception as e:
        print(f"Error calculating credit risk: {str(e)}")
        # Fallback to rule-based calculation
        return calculate_credit_risk_fallback(applicant_data)

def calculate_fraud_risk(applicant_data: Dict, extracted_data: Dict, sagemaker_runtime) -> Dict:
    """Calculate fraud risk using SageMaker model"""
    try:
        # Prepare features for fraud detection
        features = {
            'income_consistency': calculate_income_consistency(applicant_data, extracted_data),
            'document_authenticity': calculate_document_authenticity(extracted_data),
            'behavioral_patterns': calculate_behavioral_patterns(applicant_data),
            'application_velocity': calculate_application_velocity(applicant_data),
            'ip_reputation': applicant_data.get('ip_reputation', 0.8),
            'device_fingerprint': applicant_data.get('device_fingerprint', 0.7),
            'time_patterns': calculate_time_patterns(applicant_data),
            'geographic_consistency': calculate_geographic_consistency(applicant_data)
        }
        
        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='fraud-detection-model-endpoint',
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        result = json.loads(response['Body'].read())
        fraud_score = result['fraud_score']
        
        return {
            'fraud_score': fraud_score,
            'fraud_level': get_fraud_level(fraud_score),
            'is_fraud': result.get('is_fraud', False),
            'confidence': result.get('confidence', 0.85),
            'model_version': 'v1.0'
        }
        
    except Exception as e:
        print(f"Error calculating fraud risk: {str(e)}")
        return calculate_fraud_risk_fallback(applicant_data, extracted_data)

def calculate_market_risk(applicant_data: Dict) -> Dict:
    """Calculate market risk based on economic conditions"""
    try:
        # Simulate market risk calculation
        loan_amount = applicant_data.get('requested_amount', 50000)
        loan_purpose = applicant_data.get('loan_purpose', 'personal')
        
        # Base market risk
        market_risk = 0.1
        
        # Adjust based on loan amount
        if loan_amount > 100000:
            market_risk += 0.05
        elif loan_amount > 50000:
            market_risk += 0.02
        
        # Adjust based on loan purpose
        purpose_risk_multipliers = {
            'business': 1.2,
            'education': 1.1,
            'personal': 1.0,
            'debt_consolidation': 0.9,
            'home_improvement': 0.8
        }
        
        market_risk *= purpose_risk_multipliers.get(loan_purpose, 1.0)
        
        return {
            'market_risk_score': min(market_risk, 1.0),
            'market_risk_level': get_risk_level(market_risk),
            'risk_factors': ['loan_amount', 'loan_purpose'],
            'calculation_method': 'rule_based'
        }
        
    except Exception as e:
        print(f"Error calculating market risk: {str(e)}")
        return {
            'market_risk_score': 0.2,
            'market_risk_level': 'MEDIUM',
            'error': str(e)
        }

def calculate_operational_risk(applicant_data: Dict, extracted_data: Dict) -> Dict:
    """Calculate operational risk based on process and data quality"""
    try:
        operational_risk = 0.05  # Base operational risk
        
        # Check data completeness
        required_fields = ['credit_score', 'annual_income', 'employment_years', 'requested_amount']
        missing_fields = [field for field in required_fields if not applicant_data.get(field)]
        
        if missing_fields:
            operational_risk += len(missing_fields) * 0.02
        
        # Check document quality
        if extracted_data:
            avg_authenticity = 0
            doc_count = 0
            for doc_data in extracted_data.values():
                if isinstance(doc_data, dict) and 'authenticity_score' in doc_data:
                    avg_authenticity += doc_data['authenticity_score']
                    doc_count += 1
            
            if doc_count > 0:
                avg_authenticity /= doc_count
                if avg_authenticity < 0.7:
                    operational_risk += 0.1
        
        return {
            'operational_risk_score': min(operational_risk, 1.0),
            'operational_risk_level': get_risk_level(operational_risk),
            'risk_factors': ['data_completeness', 'document_quality'],
            'calculation_method': 'rule_based'
        }
        
    except Exception as e:
        print(f"Error calculating operational risk: {str(e)}")
        return {
            'operational_risk_score': 0.1,
            'operational_risk_level': 'LOW',
            'error': str(e)
        }

def calculate_overall_risk(credit_risk: float, fraud_risk: float, market_risk: float, operational_risk: float) -> float:
    """Calculate weighted overall risk score"""
    # Weighted average of different risk types
    weights = {
        'credit': 0.4,
        'fraud': 0.3,
        'market': 0.2,
        'operational': 0.1
    }
    
    overall_risk = (
        credit_risk * weights['credit'] +
        fraud_risk * weights['fraud'] +
        market_risk * weights['market'] +
        operational_risk * weights['operational']
    )
    
    return min(overall_risk, 1.0)

# Helper functions
def get_loan_purpose_score(loan_purpose: str) -> int:
    """Convert loan purpose to numeric score"""
    purpose_scores = {
        'home_improvement': 1,
        'debt_consolidation': 2,
        'business': 3,
        'education': 2,
        'personal': 4
    }
    return purpose_scores.get(loan_purpose, 3)

def get_risk_level(risk_score: float) -> str:
    """Convert risk score to risk level"""
    if risk_score < 0.2:
        return 'LOW'
    elif risk_score < 0.5:
        return 'MEDIUM'
    else:
        return 'HIGH'

def get_fraud_level(fraud_score: float) -> str:
    """Convert fraud score to fraud level"""
    if fraud_score > 0.1:
        return 'LOW'
    elif fraud_score > -0.1:
        return 'MEDIUM'
    else:
        return 'HIGH'

def calculate_income_consistency(applicant_data: Dict, extracted_data: Dict) -> float:
    """Calculate income consistency score"""
    # Simplified implementation
    return 0.8

def calculate_document_authenticity(extracted_data: Dict) -> float:
    """Calculate document authenticity score"""
    if not extracted_data:
        return 0.5
    
    authenticity_scores = []
    for doc_data in extracted_data.values():
        if isinstance(doc_data, dict) and 'authenticity_score' in doc_data:
            authenticity_scores.append(doc_data['authenticity_score'])
    
    return sum(authenticity_scores) / len(authenticity_scores) if authenticity_scores else 0.5

def calculate_behavioral_patterns(applicant_data: Dict) -> float:
    """Calculate behavioral pattern score"""
    # Simplified implementation
    return 0.7

def calculate_application_velocity(applicant_data: Dict) -> float:
    """Calculate application velocity score"""
    # Simplified implementation
    return 0.5

def calculate_time_patterns(applicant_data: Dict) -> float:
    """Calculate time pattern score"""
    # Simplified implementation
    return 0.6

def calculate_geographic_consistency(applicant_data: Dict) -> float:
    """Calculate geographic consistency score"""
    # Simplified implementation
    return 0.8

def calculate_credit_risk_fallback(applicant_data: Dict) -> Dict:
    """Fallback credit risk calculation using rules"""
    credit_score = applicant_data.get('credit_score', 650)
    debt_to_income = applicant_data.get('debt_to_income_ratio', 0.3)
    
    # Simple rule-based risk calculation
    if credit_score >= 750 and debt_to_income < 0.3:
        risk_score = 0.1
    elif credit_score >= 650 and debt_to_income < 0.4:
        risk_score = 0.3
    else:
        risk_score = 0.6
    
    return {
        'risk_score': risk_score,
        'risk_level': get_risk_level(risk_score),
        'confidence': 0.6,
        'model_version': 'fallback'
    }

def calculate_fraud_risk_fallback(applicant_data: Dict, extracted_data: Dict) -> Dict:
    """Fallback fraud risk calculation using rules"""
    # Simple rule-based fraud detection
    fraud_score = 0.0
    
    # Check for suspicious patterns
    if applicant_data.get('age', 0) < 18:
        fraud_score -= 0.5
    
    if applicant_data.get('annual_income', 0) < 10000:
        fraud_score -= 0.3
    
    return {
        'fraud_score': fraud_score,
        'fraud_level': get_fraud_level(fraud_score),
        'is_fraud': fraud_score < -0.1,
        'confidence': 0.6,
        'model_version': 'fallback'
    }
