#!/usr/bin/env python3
"""
Script to insert sample data into DynamoDB tables for testing
"""

import boto3
import json
from datetime import datetime
import uuid

def insert_sample_loan_decision():
    """Insert sample loan decision data"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Sample loan decision data
        sample_decision = {
            'application_id': str(uuid.uuid4()),
            'applicant_name': 'John Doe',
            'loan_amount': 50000,
            'decision': 'APPROVED',
            'interest_rate': 5.5,
            'loan_term_months': 60,
            'monthly_payment': 955.65,
            'credit_score': 750,
            'risk_score': 0.15,
            'decision_reason': 'Strong credit history and stable income',
            'processing_time_seconds': 45,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'COMPLETED'
        }
        
        print("📝 Inserting sample loan decision...")
        
        # Convert to DynamoDB format
        item = {}
        for key, value in sample_decision.items():
            if isinstance(value, str):
                item[key] = {'S': value}
            elif isinstance(value, (int, float)):
                item[key] = {'N': str(value)}
            elif isinstance(value, bool):
                item[key] = {'BOOL': value}
        
        # Insert into DynamoDB
        response = dynamodb.put_item(
            TableName='loan-decisions',
            Item=item
        )
        
        print(f"✅ Successfully inserted loan decision: {sample_decision['application_id']}")
        return sample_decision['application_id']
        
    except Exception as e:
        print(f"❌ Error inserting loan decision: {str(e)}")
        return None

def insert_sample_risk_assessment(application_id):
    """Insert sample risk assessment data"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Sample risk assessment data
        sample_risk = {
            'applicant_id': application_id,  # This is the primary key
            'application_id': application_id,
            'credit_risk_score': 0.15,
            'fraud_risk_score': 0.05,
            'market_risk_score': 0.10,
            'operational_risk_score': 0.08,
            'overall_risk_score': 0.12,
            'risk_level': 'LOW',
            'risk_factors': [
                'Strong credit history',
                'Stable employment',
                'Low debt-to-income ratio'
            ],
            'mitigation_strategies': [
                'Standard interest rate',
                'Regular monitoring',
                'Annual review'
            ],
            'assessment_timestamp': datetime.utcnow().isoformat(),
            'assessor': 'AI_RISK_AGENT',
            'confidence_score': 0.92
        }
        
        print("📝 Inserting sample risk assessment...")
        
        # Convert to DynamoDB format
        item = {}
        for key, value in sample_risk.items():
            if isinstance(value, str):
                item[key] = {'S': value}
            elif isinstance(value, (int, float)):
                item[key] = {'N': str(value)}
            elif isinstance(value, bool):
                item[key] = {'BOOL': value}
            elif isinstance(value, list):
                # Convert list to DynamoDB list format
                item[key] = {'L': [{'S': str(v)} for v in value]}
        
        # Insert into DynamoDB
        response = dynamodb.put_item(
            TableName='risk-assessments',
            Item=item
        )
        
        print(f"✅ Successfully inserted risk assessment: {application_id}")
        
    except Exception as e:
        print(f"❌ Error inserting risk assessment: {str(e)}")

def insert_multiple_samples():
    """Insert multiple sample records"""
    print("🚀 Inserting multiple sample records...")
    print("=" * 50)
    
    # Insert 3 sample loan decisions
    for i in range(3):
        print(f"\n📋 Creating sample {i+1}:")
        application_id = insert_sample_loan_decision()
        if application_id:
            insert_sample_risk_assessment(application_id)
        print("-" * 30)
    
    print("\n✅ Sample data insertion complete!")

if __name__ == "__main__":
    print("🚀 DynamoDB Sample Data Inserter")
    print("=" * 50)
    
    # Insert sample data
    insert_multiple_samples()
    
    print("\n💡 Now you can view the data using:")
    print("   python3 view_dynamodb_data.py")
