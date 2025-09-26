#!/usr/bin/env python3
"""
Script to check if the latest workflow execution data was stored
"""

import boto3
import json

def check_latest_record():
    """Check if the latest applicant data was stored"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Latest applicant ID from the workflow execution
        applicant_id = '9e797132-1673-420c-a604-f44eeae9d524'
        
        print(f"🔍 Checking for applicant: {applicant_id}")
        print("=" * 60)
        
        # Check loan-decisions table
        print("📋 Checking loan-decisions table...")
        try:
            decision_response = dynamodb.get_item(
                TableName='loan-decisions',
                Key={'application_id': {'S': applicant_id}}
            )
            if 'Item' in decision_response:
                print("✅ Loan decision found!")
                print(json.dumps(decision_response['Item'], indent=2))
            else:
                print("❌ No loan decision found")
        except Exception as e:
            print(f"❌ Error checking loan-decisions table: {e}")

        print("\n📋 Checking risk-assessments table...")
        try:
            risk_response = dynamodb.get_item(
                TableName='risk-assessments',
                Key={'applicant_id': {'S': applicant_id}}
            )
            if 'Item' in risk_response:
                print("✅ Risk assessment found!")
                print(json.dumps(risk_response['Item'], indent=2))
            else:
                print("❌ No risk assessment found")
        except Exception as e:
            print(f"❌ Error checking risk-assessments table: {e}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    check_latest_record()
