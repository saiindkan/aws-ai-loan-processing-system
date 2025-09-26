#!/usr/bin/env python3
"""
Script to query specific records from DynamoDB tables
"""

import boto3
import json
from datetime import datetime

def query_loan_decision(application_id):
    """Query a specific loan decision by application_id"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print(f"🔍 Querying loan decision for application: {application_id}")
        print("=" * 60)
        
        # Query the table
        response = dynamodb.get_item(
            TableName='loan-decisions',
            Key={
                'application_id': {'S': application_id}
            }
        )
        
        item = response.get('Item')
        
        if not item:
            print(f"❌ No loan decision found for application: {application_id}")
            return None
        
        # Parse DynamoDB item format
        parsed_item = {}
        for key, value in item.items():
            if 'S' in value:
                parsed_item[key] = value['S']
            elif 'N' in value:
                parsed_item[key] = value['N']
            elif 'BOOL' in value:
                parsed_item[key] = value['BOOL']
            elif 'M' in value:
                parsed_item[key] = value['M']
            else:
                parsed_item[key] = value
        
        # Pretty print the item
        print("📋 Loan Decision Details:")
        print("-" * 40)
        print(json.dumps(parsed_item, indent=2, default=str))
        
        return parsed_item
        
    except Exception as e:
        print(f"❌ Error querying loan decision: {str(e)}")
        return None

def query_risk_assessment(applicant_id):
    """Query a specific risk assessment by applicant_id"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print(f"\n🔍 Querying risk assessment for applicant: {applicant_id}")
        print("=" * 60)
        
        # Query the table
        response = dynamodb.get_item(
            TableName='risk-assessments',
            Key={
                'applicant_id': {'S': applicant_id}
            }
        )
        
        item = response.get('Item')
        
        if not item:
            print(f"❌ No risk assessment found for applicant: {applicant_id}")
            return None
        
        # Parse DynamoDB item format
        parsed_item = {}
        for key, value in item.items():
            if 'S' in value:
                parsed_item[key] = value['S']
            elif 'N' in value:
                parsed_item[key] = value['N']
            elif 'BOOL' in value:
                parsed_item[key] = value['BOOL']
            elif 'M' in value:
                parsed_item[key] = value['M']
            elif 'L' in value:
                # Handle lists
                parsed_item[key] = [v['S'] for v in value['L']]
            else:
                parsed_item[key] = value
        
        # Pretty print the item
        print("📋 Risk Assessment Details:")
        print("-" * 40)
        print(json.dumps(parsed_item, indent=2, default=str))
        
        return parsed_item
        
    except Exception as e:
        print(f"❌ Error querying risk assessment: {str(e)}")
        return None

def query_complete_application(application_id):
    """Query both loan decision and risk assessment for a complete view"""
    print("🚀 Complete Application Query")
    print("=" * 60)
    
    # Query loan decision
    loan_decision = query_loan_decision(application_id)
    
    if loan_decision:
        # Query risk assessment using the same ID
        risk_assessment = query_risk_assessment(application_id)
        
        if risk_assessment:
            print("\n✅ Complete application data retrieved successfully!")
            
            # Summary
            print("\n📊 Application Summary:")
            print("-" * 40)
            print(f"Application ID: {application_id}")
            print(f"Applicant: {loan_decision.get('applicant_name', 'N/A')}")
            print(f"Loan Amount: ${loan_decision.get('loan_amount', 'N/A')}")
            print(f"Decision: {loan_decision.get('decision', 'N/A')}")
            print(f"Interest Rate: {loan_decision.get('interest_rate', 'N/A')}%")
            print(f"Risk Level: {risk_assessment.get('risk_level', 'N/A')}")
            print(f"Overall Risk Score: {risk_assessment.get('overall_risk_score', 'N/A')}")
            print(f"Processing Time: {loan_decision.get('processing_time_seconds', 'N/A')} seconds")
        else:
            print("❌ Risk assessment not found")
    else:
        print("❌ Loan decision not found")

if __name__ == "__main__":
    print("🚀 DynamoDB Specific Record Query")
    print("=" * 60)
    
    # Example: Query the first application ID from our sample data
    sample_application_id = "1756af71-54dd-4e66-b312-2096183bc20a"
    
    print(f"📋 Querying sample application: {sample_application_id}")
    query_complete_application(sample_application_id)
    
    print("\n💡 To query a different application, modify the application_id in the script")
