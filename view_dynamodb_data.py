#!/usr/bin/env python3
"""
Script to view data in DynamoDB loan-decisions table
"""

import boto3
import json
from datetime import datetime

def view_loan_decisions():
    """View all data in the loan-decisions table"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print("🔍 Scanning loan-decisions table...")
        print("=" * 50)
        
        # Scan the table
        response = dynamodb.scan(
            TableName='loan-decisions',
            Select='ALL_ATTRIBUTES'
        )
        
        items = response.get('Items', [])
        
        if not items:
            print("❌ No data found in loan-decisions table")
            return
        
        print(f"✅ Found {len(items)} records in loan-decisions table")
        print("=" * 50)
        
        # Display each item
        for i, item in enumerate(items, 1):
            print(f"\n📋 Record {i}:")
            print("-" * 30)
            
            # Parse DynamoDB item format
            parsed_item = {}
            for key, value in item.items():
                # DynamoDB stores values as {'S': 'string_value'} or {'N': '123'}
                if 'S' in value:
                    parsed_item[key] = value['S']
                elif 'N' in value:
                    parsed_item[key] = value['N']
                elif 'BOOL' in value:
                    parsed_item[key] = value['BOOL']
                elif 'M' in value:
                    # Handle nested maps
                    parsed_item[key] = value['M']
                else:
                    parsed_item[key] = value
            
            # Pretty print the item
            print(json.dumps(parsed_item, indent=2, default=str))
            
        print("\n" + "=" * 50)
        print(f"📊 Total records: {len(items)}")
        
    except Exception as e:
        print(f"❌ Error viewing DynamoDB data: {str(e)}")
        print("\n💡 Make sure:")
        print("   1. AWS credentials are configured")
        print("   2. You have permission to read the table")
        print("   3. The table exists in us-east-1 region")

def view_risk_assessments():
    """View all data in the risk-assessments table"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print("\n🔍 Scanning risk-assessments table...")
        print("=" * 50)
        
        # Scan the table
        response = dynamodb.scan(
            TableName='risk-assessments',
            Select='ALL_ATTRIBUTES'
        )
        
        items = response.get('Items', [])
        
        if not items:
            print("❌ No data found in risk-assessments table")
            return
        
        print(f"✅ Found {len(items)} records in risk-assessments table")
        print("=" * 50)
        
        # Display each item
        for i, item in enumerate(items, 1):
            print(f"\n📋 Record {i}:")
            print("-" * 30)
            
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
            print(json.dumps(parsed_item, indent=2, default=str))
            
        print("\n" + "=" * 50)
        print(f"📊 Total records: {len(items)}")
        
    except Exception as e:
        print(f"❌ Error viewing risk-assessments data: {str(e)}")

if __name__ == "__main__":
    print("🚀 DynamoDB Data Viewer")
    print("=" * 50)
    
    # View loan-decisions table
    view_loan_decisions()
    
    # View risk-assessments table
    view_risk_assessments()
    
    print("\n✅ Data viewing complete!")
